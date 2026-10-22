"""AROME and ARPEGE packages of Météo-France (S3 bucket ``meteofrance-pnt``, no index).

For each package the S3 listing gives the files (one per group of steps), their
size and deposit time; the headers of every message are read by byte ranges, the
messages of the catalogue are selected by GRIB2 identity, fetched by coalesced
ranges and decoded by eccodes, which gives the authoritative step and keys.
"""

import re
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
from powatlas.gribheaders import coalesce, walk_messages
from powatlas.http import HttpClient, HttpError
from powatlas.units import Unit
from powatlas.writer import Fetched, Manifest, write_forecast_unit

HEAD_BYTES = 1024  # sections 0 to 4 of Météo-France messages fit in less (inspection of 2026-10-22)
LEVEL_TOLERANCE = 1e-6
_GROUP = re.compile(r"__(\d{2,3})H(\d{2,3})H__")
_CONTENTS = re.compile(r"<Contents>(.*?)</Contents>", re.S)


def group_steps(file_name: str) -> tuple[int, int]:
    m = _GROUP.search(file_name)
    if m is None:
        raise FormatChange(f"no step group in file name {file_name}")
    return int(m[1]), int(m[2])


def _listing(source: Source, run: datetime, package: str, http: HttpClient) -> list[tuple[str, int]]:
    """(url, size) of the files of one package of one run."""
    prefix = source.urls["prefix"].format(iso=run.strftime("%Y-%m-%dT%H:%M:%SZ"), package=package)
    xml = http.get(f"{source.urls['base']}?list-type=2&prefix={prefix}").content.decode("utf-8")
    files = []
    for block in _CONTENTS.findall(xml):
        key = re.search(r"<Key>(.*?)</Key>", block)[1]
        size = int(re.search(r"<Size>(\d+)</Size>", block)[1])
        files.append((source.urls["base"] + key, size))
    if "<IsTruncated>true</IsTruncated>" in xml:
        raise FormatChange(f"listing of {prefix} truncated: more than one page")
    return files


def _matches(head, grib: list) -> bool:
    d, c, n, lt, lv = grib
    if (head.discipline, head.category, head.number, head.level_type) != (d, c, n, lt):
        return False
    if lv is None or head.level_value is None:
        return lv is None and head.level_value is None
    return abs(head.level_value - lv) <= LEVEL_TOLERANCE


class MeteoFrancePntAdapter:
    def collect(
        self, unit: Unit, source: Source, http: HttpClient, out_dir: Path, mode: str, settings: dict
    ) -> Manifest:
        start = datetime.now(timezone.utc)
        bbox = BBox(*settings["bbox"])
        expected = expected_pairs(source)
        wanted_steps: dict[str, set[int]] = {}
        for v, s in expected:
            wanted_steps.setdefault(v, set()).add(s)
        fields: dict[tuple[str, int], Field] = {}
        fetched: list[Fetched] = []
        notes: list[str] = []
        packages = sorted({spec["package"] for spec in source.variables.values()})
        try:
            for package in packages:
                pvars = {v: spec for v, spec in source.variables.items() if spec["package"] == package}
                try:
                    files = _listing(source, unit.ref, package, http)
                except HttpError as exc:
                    notes.append(f"{package}: listing failed ({exc})")
                    continue
                for url, size in files:
                    first, last = group_steps(url)
                    if not any(first <= s <= last for steps in wanted_steps.values() for s in steps):
                        continue
                    self._collect_file(url, size, pvars, unit, source, http, bbox, settings, wanted_steps,
                                       fields, fetched, notes)
        except (GridMismatch, FormatChange) as exc:
            notes.append(f"{type(exc).__name__}: {exc}")
            fields = {}
        return write_forecast_unit(out_dir, unit, source, fields, expected, fetched, mode, None, start, notes)

    @staticmethod
    def _collect_file(url, size, pvars, unit, source, http, bbox, settings, wanted_steps, fields, fetched, notes):
        name = url.rsplit("/", 1)[1]
        try:
            heads = walk_messages(http, url, size, HEAD_BYTES)
        except (HttpError, ValueError) as exc:
            notes.append(f"{name}: headers unreadable ({exc})")
            return
        selected = []
        for h in heads:
            hits = [v for v, spec in pvars.items() if _matches(h, spec["grib"])]
            if len(hits) > 1:
                raise FormatChange(f"{name}: message at {h.offset} matches several variables {hits}")
            if hits:
                selected.append((h, hits[0]))
        for first, last in coalesce([(h.offset, h.offset + h.length - 1) for h, _ in selected]):
            try:
                r = http.get(url, byte_range=(first, last))
            except HttpError as exc:
                notes.append(f"{name}: bytes {first}-{last}: {exc}")
                continue
            stale = False
            for h, var in selected:
                if not first <= h.offset <= last:
                    continue
                msg = r.content[h.offset - first : h.offset - first + h.length]
                try:
                    (f,) = iter_fields(msg)
                except TruncatedMessage as exc:
                    notes.append(f"{name}: {var} at {h.offset}: {exc}")
                    continue
                except ValueError as exc:
                    raise FormatChange(f"{name}: {var} at {h.offset}: {exc}") from exc
                if f.short_name != pvars[var]["shortName"]:
                    raise FormatChange(f"{name}: shortName {f.short_name} instead of {pvars[var]['shortName']}")
                if f.step_end not in wanted_steps[var]:
                    notes.append(f"{name}: {var} at step {f.step_end_minutes} min not in the catalogue, ignored")
                    continue
                try:
                    check_ref_time(f, unit.ref)
                except RefTimeMismatch as exc:
                    notes.append(f"stale message skipped: {exc}")
                    stale = True
                    continue
                check_grid(f, source.grid)
                if (var, f.step_end) in fields:
                    raise FormatChange(f"{name}: two messages for {var}@{f.step_end}")
                fields[(var, f.step_end)] = crop_field(f, bbox, settings["margin_cells"])
            fetched.append(Fetched(f"{url}#bytes={first}-{last}", r.last_modified, len(r.content), rejected=stale))


ADAPTERS["meteofrance-pnt"] = MeteoFrancePntAdapter()
