"""GFS 0.25 degree from the NOAA open data bucket on AWS (backfill and weekly catch-up on the PC).

Records are selected in the ``.idx`` file by variable, level and time
description: "instant" means "N hour fcst" (or "anl" at step 0),
"acc-from-run-start" means "0-N hour acc fcst" or "0-D day acc fcst". The 3 h
files list the 0-3 h accumulation twice (bucket and total, same period): the
first record is kept.
"""

import re
from datetime import datetime, timezone
from pathlib import Path

from powatlas.adapters import ADAPTERS, out_of_time
from powatlas.adapters.dwd_icon import FormatChange
from powatlas.catalogue import Source, expected_pairs
from powatlas.domain import BBox
from powatlas.grib import (
    Field,
    GridMismatch,
    RefTimeMismatch,
    TruncatedMessage,
    check_grid,
    check_ref_time,
    crop_field,
    iter_fields,
)
from powatlas.gribheaders import coalesce
from powatlas.http import HttpClient, HttpError, NotFound
from powatlas.indexes import parse_gfs_idx
from powatlas.units import Unit
from powatlas.writer import Fetched, Manifest, write_forecast_unit

BUCKET = "https://noaa-gfs-bdp-pds.s3.amazonaws.com/"
_INSTANT = re.compile(r"^(anl|\d+ hour fcst)$")
_ACC0 = re.compile(r"^0-\d+ (hour|day) acc fcst$")


def gfs_url(run: datetime, step: int) -> str:
    return f"{BUCKET}gfs.{run:%Y%m%d}/{run:%H}/atmos/gfs.t{run:%H}z.pgrb2.0p25.f{step:03d}"


def _time_ok(kind: str, desc: str) -> bool:
    if kind == "instant":
        return bool(_INSTANT.match(desc))
    if kind == "acc-from-run-start":
        return bool(_ACC0.match(desc))
    raise ValueError(f"unknown time kind {kind}")


def _drop_unpublished(expected, unpublished, notes):
    """Backfill: a field absent from the index at a date was not published then; it is
    listed in the notes and not expected, instead of making the unit partial."""
    if not unpublished:
        return expected
    by_var: dict[str, list[int]] = {}
    for var, step in sorted(unpublished):
        by_var.setdefault(var, []).append(step)
    for var, steps in by_var.items():
        notes.append(f"not published at this date (absent from the index): {var} at {len(steps)} steps")
    return [p for p in expected if p not in unpublished]


class GfsAdapter:
    def collect(
        self, unit: Unit, source: Source, http: HttpClient, out_dir: Path, mode: str, settings: dict
    ) -> Manifest:
        start = datetime.now(timezone.utc)
        bbox = BBox(*settings["bbox"])
        expected = expected_pairs(source)
        fields: dict[tuple[str, int], Field] = {}
        fetched: list[Fetched] = []
        notes: list[str] = []
        unpublished: set[tuple[str, int]] = set()  # backfill only: absent from the producer's index
        try:
            for step in source.steps:
                if out_of_time(start, settings):
                    notes.append("time budget exhausted: unit written as it stands")
                    break
                wanted = [v for v, s in expected if s == step]
                if wanted:
                    self._collect_step(step, wanted, unit, source, http, bbox, settings, fields, fetched, notes,
                                       unpublished, mode)
        except (GridMismatch, FormatChange) as exc:
            notes.append(f"{type(exc).__name__}: {exc}")
            fields = {}
        expected = _drop_unpublished(expected, unpublished, notes)
        return write_forecast_unit(out_dir, unit, source, fields, expected, fetched, mode, "atmos/pgrb2.0p25",
                                   start, notes)

    @staticmethod
    def _collect_step(step, wanted, unit, source, http, bbox, settings, fields, fetched, notes, unpublished, mode):
        url = gfs_url(unit.ref, step)
        try:
            entries = parse_gfs_idx(http.get(url + ".idx").content)
        except NotFound:
            notes.append(f"step {step}: no idx")
            return
        except (HttpError, ValueError) as exc:
            notes.append(f"step {step}: idx unreadable ({exc})")
            return
        selected = []
        for var in wanted:
            spec = source.variables[var]
            hits = [e for e in entries if e.var == spec["var"] and e.level == spec["level"]
                    and _time_ok(spec["time"], e.desc)]
            if len({e.desc for e in hits}) > 1:
                raise FormatChange(f"step {step}: {var} matches records {sorted({e.desc for e in hits})}")
            if not hits and mode == "backfill":
                unpublished.add((var, step))
            if hits:
                if hits[0].length is None:
                    raise FormatChange(f"step {step}: {var} is the last idx record, length unknown")
                selected.append((hits[0], var))
        for first, last in coalesce([(e.offset, e.offset + e.length - 1) for e, _ in selected]):
            try:
                r = http.get(url, byte_range=(first, last))
            except HttpError as exc:
                notes.append(f"step {step}: bytes {first}-{last}: {exc}")
                continue
            in_range = stale_count = 0
            for e, var in selected:
                if not first <= e.offset <= last:
                    continue
                in_range += 1
                part = r.content[e.offset - first : e.offset - first + e.length]
                try:
                    (f,) = iter_fields(part)
                except TruncatedMessage as exc:
                    notes.append(f"step {step}: {var}: {exc}")
                    continue
                except ValueError as exc:
                    raise FormatChange(f"step {step}: {var}: {exc}") from exc
                if f.short_name != source.variables[var]["shortName"] or f.step_end != step:
                    raise FormatChange(f"step {step}: {var} decoded as {f.short_name} at {f.step_end_minutes} min")
                try:
                    check_ref_time(f, unit.ref)
                except RefTimeMismatch as exc:
                    notes.append(f"stale message skipped: {exc}")
                    stale_count += 1
                    continue
                check_grid(f, source.grid)
                fields[(var, step)] = crop_field(f, bbox, settings["margin_cells"])
            rejected = in_range > 0 and stale_count == in_range
            fetched.append(Fetched(f"{url}#bytes={first}-{last}", r.last_modified, len(r.content), rejected=rejected))


ADAPTERS["gfs"] = GfsAdapter()
