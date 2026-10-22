"""ECMWF open data (IFS and AIFS Single, 0.25 degree): index plus byte ranges per step file.

Daily collection reads the portal (data.ecmwf.int, about 4 days kept); the AWS
copy (same paths) serves the historical backfill. Only index entries whose step
equals the file's step are used: the 0 h index also lists the 0-3 h minimum and
maximum temperatures, which belong to step 3.
"""

from datetime import datetime, timezone
from pathlib import Path

from powatlas.adapters import ADAPTERS
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
        try:
            for step in source.steps:
                wanted = [v for v, s in expected if s == step]
                if wanted:
                    self._collect_step(base, step, wanted, unit, source, http, bbox, settings, fields, fetched, notes)
        except (GridMismatch, FormatChange) as exc:
            notes.append(f"{type(exc).__name__}: {exc}")
            fields = {}
        stream = f"{source.urls['model']}/0p25/oper"
        return write_forecast_unit(out_dir, unit, source, fields, expected, fetched, mode, stream, start, notes)

    @staticmethod
    def _collect_step(base, step, wanted, unit, source, http, bbox, settings, fields, fetched, notes):
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
        for first, last in coalesce([(e.offset, e.offset + e.length - 1) for e, _ in selected]):
            try:
                r = http.get(url + ".grib2", byte_range=(first, last))
            except HttpError as exc:
                notes.append(f"step {step}: bytes {first}-{last}: {exc}")
                continue
            stale = False
            for e, var in selected:
                if not first <= e.offset <= last:
                    continue
                part = r.content[e.offset - first : e.offset - first + e.length]
                try:
                    (f,) = iter_fields(part)
                except TruncatedMessage as exc:
                    notes.append(f"step {step}: {var}: {exc}")
                    continue
                except ValueError as exc:
                    raise FormatChange(f"step {step}: {var}: {exc}") from exc
                if f.short_name != source.variables[var]["param"] or f.step_end != step:
                    raise FormatChange(f"step {step}: {var} decoded as {f.short_name} at {f.step_end_minutes} min")
                try:
                    check_ref_time(f, unit.ref)
                except RefTimeMismatch as exc:
                    notes.append(f"stale message skipped: {exc}")
                    stale = True
                    continue
                check_grid(f, source.grid)
                fields[(var, step)] = crop_field(f, bbox, settings["margin_cells"])
            fetched.append(Fetched(f"{url}.grib2#bytes={first}-{last}", r.last_modified, len(r.content), rejected=stale))


ADAPTERS["ecmwf"] = EcmwfAdapter()
