"""ICON-D2 and ICON-EU from opendata.dwd.de: one bzip2 GRIB2 file per variable and step.

Only the message at the whole hour is kept (ICON-D2 files also hold three
quarter-hour messages, see docs/sources/icon-dwd.md). Files still holding the
previous day's run are rejected by the run check; the unit is then partial and
the second trigger retries it.
"""

import bz2
from datetime import datetime, timezone
from pathlib import Path

from powatlas.adapters import ADAPTERS, out_of_time
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
from powatlas.http import HttpClient, HttpError, NotFound
from powatlas.units import Unit
from powatlas.writer import Fetched, Manifest, write_forecast_unit


class FormatChange(ValueError):
    """A file no longer has the structure documented in the source record."""


def icon_url(source: Source, run: datetime, variable: str, step: int) -> str:
    return source.urls["file"].format(
        HH=f"{run.hour:02d}", run=run.strftime("%Y%m%d%H"), step=f"{step:03d}", var=variable, VAR=variable.upper()
    )


def _select(data: bytes, variable: str, step: int, selector: dict) -> Field:
    """The single whole-hour message of a decompressed file.

    TruncatedMessage propagates (transient: the pair is only absent); any other
    decoding error or an unexpected structure is a FormatChange.
    """
    try:
        decoded = list(iter_fields(data))
    except TruncatedMessage:
        raise
    except ValueError as exc:  # unsupported grid or scanning mode, inconsistent grid
        raise FormatChange(f"{variable}@{step}: {exc}") from exc
    hourly = [f for f in decoded if f.step_end == step]
    if len(hourly) != 1:
        raise FormatChange(f"{variable}@{step}: {len(hourly)} messages at the whole hour instead of 1")
    f = hourly[0]
    if f.short_name != selector["shortName"]:
        raise FormatChange(f"{variable}@{step}: shortName {f.short_name} instead of {selector['shortName']}")
    return f


class DwdIconAdapter:
    def collect(
        self, unit: Unit, source: Source, http: HttpClient, out_dir: Path, mode: str, settings: dict
    ) -> Manifest:
        start = datetime.now(timezone.utc)
        bbox = BBox(*settings["bbox"])
        expected = expected_pairs(source)
        fields: dict[tuple[str, int], Field] = {}
        fetched: list[Fetched] = []
        notes: list[str] = []
        not_found = 0
        try:
            for variable, step in expected:
                if out_of_time(start, settings):
                    notes.append("time budget exhausted: unit written as it stands")
                    break
                url = icon_url(source, unit.ref, variable, step)
                try:
                    r = http.get(url)
                except NotFound:
                    not_found += 1
                    continue
                except HttpError as exc:
                    notes.append(f"{variable}@{step}: {exc}")
                    continue
                try:
                    data = bz2.decompress(r.content)
                    f = _select(data, variable, step, source.variables[variable])
                except (OSError, EOFError, TruncatedMessage) as exc:
                    # bz2 raises OSError on a non-bzip2 body (error page), EOFError or
                    # ValueError on a cut stream: transient, the pair is absent.
                    notes.append(f"{variable}@{step}: unreadable file ({type(exc).__name__}: {exc})")
                    fetched.append(Fetched(url, r.last_modified, len(r.content), rejected=True))
                    continue
                except ValueError as exc:
                    if isinstance(exc, FormatChange):
                        raise
                    notes.append(f"{variable}@{step}: unreadable file ({exc})")
                    fetched.append(Fetched(url, r.last_modified, len(r.content), rejected=True))
                    continue
                try:
                    check_ref_time(f, unit.ref)
                except RefTimeMismatch as exc:
                    notes.append(f"stale file skipped: {exc}")
                    fetched.append(Fetched(url, r.last_modified, len(r.content), rejected=True))
                    continue
                check_grid(f, source.grid)
                fetched.append(Fetched(url, r.last_modified, len(r.content)))
                fields[(variable, step)] = crop_field(f, bbox, settings["margin_cells"])
        except (GridMismatch, FormatChange) as exc:
            # A structural change at the producer: archive nothing rather than a mixed unit.
            notes.append(f"{type(exc).__name__}: {exc}")
            fields = {}
        if not_found:
            notes.append(f"HTTP 404 for {'all ' if not_found == len(expected) else ''}{not_found} of {len(expected)} files")
        return write_forecast_unit(out_dir, unit, source, fields, expected, fetched, mode, None, start, notes)


ADAPTERS["dwd-icon"] = DwdIconAdapter()
