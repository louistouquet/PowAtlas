"""ECMWF open data (IFS and AIFS Single, 0.25 degree): index plus byte ranges per step file.

Daily collection reads the portal (data.ecmwf.int, about 4 days kept); the AWS
copy (same paths) serves the historical backfill. Only index entries whose step
equals the file's step are used: the 0 h index also lists the 0-3 h minimum and
maximum temperatures, which belong to step 3.
"""

from datetime import datetime, timezone
from pathlib import Path

from powatlas.adapters import ADAPTERS, accumulation_from_run_start, out_of_time
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
from powatlas.indexes import parse_ecmwf_index
from powatlas.units import Unit
from powatlas.writer import Fetched, Manifest, write_forecast_unit

# Until 2024-02-28 the AWS copy had no model level in its paths (docs/sources/ecmwf-open-data.md).
LAYOUT_SWITCH = datetime(2024, 2, 29, tzinfo=timezone.utc)


def ecmwf_path(model: str, run: datetime, step: int) -> str:
    """Path, without extension, of one step file of a 00/06/12/18 UTC run."""
    day, hh = run.strftime("%Y%m%d"), f"{run.hour:02d}"
    stem = f"{day}{hh}0000-{step}h-oper-fc"
    if run < LAYOUT_SWITCH:
        if model != "ifs":
            raise ValueError(f"no {model} before {LAYOUT_SWITCH:%Y-%m-%d} in the retained archive")
        return f"{day}/{hh}z/0p25/oper/{stem}"
    return f"{day}/{hh}z/{model}/0p25/oper/{stem}"


def _drop_unpublished(expected, unpublished, notes):
    """Backfill: a variable absent from the producer's index at every step of the unit was
    not published at that date (e.g. sf before 2025-11-22): it is noted and not expected.
    Absent at only some steps, it stays expected: a cut index is a loss, not a gap."""
    if not unpublished:
        return expected
    steps_of: dict[str, set[int]] = {}
    for var, step in expected:
        steps_of.setdefault(var, set()).add(step)
    dropped = set()
    for var, steps in steps_of.items():
        absent = {s for v, s in unpublished if v == var}
        if absent and absent == steps:
            dropped.add(var)
            notes.append(f"not published at this date (absent from the index at all {len(steps)} steps): {var}")
    return [p for p in expected if p[0] not in dropped]

class EcmwfAdapter:
    def collect(
        self, unit: Unit, source: Source, http: HttpClient, out_dir: Path, mode: str, settings: dict
    ) -> Manifest:
        start = datetime.now(timezone.utc)
        bbox = BBox(*settings["bbox"])
        expected = expected_pairs(source)
        base = source.urls["aws"] if mode == "backfill" else source.urls["portal"]
        fields: dict[tuple[str, int], Field] = {}
        fetched: list[Fetched] = []
        notes: list[str] = []
        unpublished: set[tuple[str, int]] = set()  # backfill only: absent from the producer's index
        first_run = datetime.fromisoformat(source.urls["first_run"]).replace(tzinfo=timezone.utc)
        if unit.ref < first_run:
            notes.append(f"{source.urls['model']} 0.25 degree open data starts on {first_run:%Y-%m-%d}: nothing to fetch")
            return write_forecast_unit(out_dir, unit, source, {}, expected, [], mode, None, start, notes)
        try:
            for step in source.steps:
                if out_of_time(start, settings):
                    notes.append("time budget exhausted: unit written as it stands")
                    break
                wanted = [v for v, s in expected if s == step]
                if wanted:
                    self._collect_step(base, step, wanted, unit, source, http, bbox, settings, fields, fetched, notes,
                                       start, unpublished, mode)
            _check_one_encoding(fields)
        except (GridMismatch, FormatChange) as exc:
            notes.append(f"{type(exc).__name__}: {exc}")
            fields = {}
        expected = _drop_unpublished(expected, unpublished, notes)
        stream = f"{source.urls['model']}/0p25/oper"
        return write_forecast_unit(out_dir, unit, source, fields, expected, fetched, mode, stream, start, notes)

    @staticmethod
    def _collect_step(base, step, wanted, unit, source, http, bbox, settings, fields, fetched, notes, start,
                      unpublished, mode):
        url = base + ecmwf_path(source.urls["model"], unit.ref, step)
        try:
            index = parse_ecmwf_index(http.get(url + ".index").content)
        except NotFound:
            notes.append(f"step {step}: no index")
            return
        except (HttpError, ValueError, KeyError) as exc:
            notes.append(f"step {step}: index unreadable ({exc})")
            return
        selected = []
        for var in wanted:
            spec = source.variables[var]
            hits = [e for e in index if e.param == spec["param"] and e.levtype == spec["levtype"]
                    and e.levelist == spec.get("levelist") and e.step == str(step)]
            if len(hits) > 1:
                raise FormatChange(f"step {step}: {len(hits)} index entries for {var}")
            if hits:
                selected.append((hits[0], var))
            elif mode == "backfill":
                unpublished.add((var, step))
        for first, last in coalesce([(e.offset, e.offset + e.length - 1) for e, _ in selected]):
            if out_of_time(start, settings):
                return  # the caller notes the exhausted budget
            try:
                r = http.get(url + ".grib2", byte_range=(first, last))
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
                if not _same_parameter(f, source.variables[var]["param"]) or f.step_end != step:
                    raise FormatChange(f"step {step}: {var} decoded as {f.short_name} at {f.step_end_minutes} min")
                if not accumulation_from_run_start(f.keys):
                    raise FormatChange(f"step {step}: {var} accumulated over {f.keys['stepRange']}, not from the run start")
                try:
                    check_ref_time(f, unit.ref)
                except RefTimeMismatch as exc:
                    notes.append(f"stale message skipped: {exc}")
                    stale_count += 1
                    continue
                check_grid(f, source.grid, bbox, settings["margin_cells"])
                fields[(var, step)] = crop_field(f, bbox, settings["margin_cells"])
            rejected = in_range > 0 and stale_count == in_range
            fetched.append(Fetched(f"{url}.grib2#bytes={first}-{last}", r.last_modified, len(r.content), rejected=rejected))


# On AWS, the 3- and 6-hourly 2 m temperature extremes of runs from 2025-04-15 (at the latest) to
# 2026-02-01 (at least) carry GRIB2 tables version 34, which ecCodes 2.50 reads as generic time
# extremes of 2t (max_2t 237167, min_2t 238167); runs of 2024-11-15, 2026-04-15 and 2026-10-26
# carry tables 32 or 33, read as mx2t3 (228026). Section 4 is otherwise identical (checked
# 2026-10-27). The index still names them mx2t3: accepted when kind and period match.
GENERIC_EXTREMES = {"mx2t3": ("max_2t", "max", 3), "mn2t3": ("min_2t", "min", 3),
                    "mx2t6": ("max_2t", "max", 6), "mn2t6": ("min_2t", "min", 6)}


def _same_parameter(f, param: str) -> bool:
    if f.short_name == param:
        return True
    if param not in GENERIC_EXTREMES:
        return False
    short_name, step_type, hours = GENERIC_EXTREMES[param]
    return (f.short_name == short_name and f.keys.get("stepType") == step_type
            and str(f.keys.get("stepRange")) == f"{f.step_end - hours}-{f.step_end}")


def _check_one_encoding(fields: dict) -> None:
    """Both encodings of an extreme accepted, but never mixed within a run (the writer requires one
    GRIB identity per variable)."""
    names: dict[str, set] = {}
    for (var, _), f in fields.items():
        names.setdefault(var, set()).add(f.short_name)
    for var, found in names.items():
        if len(found) > 1:
            raise FormatChange(f"{var}: encodings mixed within the run ({', '.join(sorted(found))})")


ADAPTERS["ecmwf"] = EcmwfAdapter()
