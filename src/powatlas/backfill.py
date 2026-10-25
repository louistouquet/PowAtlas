"""Historical backfill from the AWS copies (run on the pilot's PC).

``probe`` measures the sustained request rate first: the AWS bucket of ECMWF
answered ``SlowDown`` from the cloud session (spec, section 2), so the
feasibility of the ~386 000 range requests is measured before committing to them.
"""

import dataclasses
import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from powatlas import adapters
from powatlas.catalogue import Source
from powatlas.http import HttpClient
from powatlas.indexes import parse_ecmwf_index
from powatlas.units import Unit, unit_id
from powatlas.writer import sha256_file


@dataclass(frozen=True)
class ProbeResult:
    requests: int
    seconds: float
    slowdowns: int  # retries absorbed by the client (SlowDown, 429, 5xx, cut connections)
    bytes: int


def probe(http: HttpClient, urls: list[str], ranges_per_url: int, clock: Callable[[], float] = time.monotonic) -> ProbeResult:
    """Read the index of each ECMWF step file (path without extension) and its first ranges."""
    t0 = clock()
    retries0 = http.retry_count
    requests = size = 0
    for url in urls:
        index = http.get(url + ".index").content
        requests += 1
        size += len(index)
        for e in parse_ecmwf_index(index)[:ranges_per_url]:
            size += len(http.get(url + ".grib2", byte_range=(e.offset, e.offset + e.length - 1)).content)
            requests += 1
    return ProbeResult(requests, clock() - t0, http.retry_count - retries0, size)


MAX_ATTEMPTS = 3  # a unit still partial after this many backfills is given up (noted in its manifest)
# Passes left partial only because the server throttled (retries exhausted on SlowDown/5xx):
# not counted as attempts, but bounded so that a unit cannot be retried forever.
MAX_THROTTLED_PASSES = 10


@dataclass
class BackfillResult:
    done: int = 0
    skipped: int = 0  # already complete in the archive (files present, sha256 checked)
    partial: int = 0
    given_up: int = 0  # still partial after MAX_ATTEMPTS
    stopped: bool = False  # max_hours reached


def last_available_day(source: Source, now: datetime) -> date:
    """Last day whose 00 UTC run is published at ``now``."""
    return (now - timedelta(hours=source.available_after_hours)).date()


def _existing(manifest: Path) -> dict | None:
    """Readable manifest whose files are all present and intact, else None (unit collected again)."""
    try:
        m = json.loads(manifest.read_text(encoding="utf-8"))
        state = m["state"]
        files = m["files"]
    except (OSError, ValueError, KeyError) as exc:
        print(f"{manifest.name}: unreadable manifest, collected again ({exc})")
        return None
    for f in files:
        path = manifest.parent / f["name"]
        if not path.is_file() or sha256_file(path) != f["sha256"]:
            print(f"{manifest.name}: {f['name']} absent or altered, collected again")
            return None
    return {"state": state, "attempts": int(m.get("attempts", 1)),
            "throttled_passes": int(m.get("throttled_passes", 0))}


def restrict_to_max_step(source: Source, max_step: int) -> Source:
    """Source limited to steps <= max_step (variables whose steps all exceed it are dropped)."""
    variables = {}
    for var, spec in source.variables.items():
        if "steps" not in spec:
            variables[var] = spec
            continue
        ranges = [[a, min(b, max_step - (max_step - a) % s), s] for a, b, s in spec["steps"] if a <= max_step]
        if ranges:
            variables[var] = dict(spec, steps=ranges)
    return dataclasses.replace(source, steps=tuple(s for s in source.steps if s <= max_step), variables=variables)


def backfill(
    source: Source,
    start: date,
    end: date,
    data_dir: Path,
    http: HttpClient,
    settings: dict,
    months: tuple[int, ...],
    max_step: int,
    max_hours: float | None,
    clock: Callable[[], float] = time.monotonic,
    retry_given_up: bool = False,
) -> BackfillResult:
    """Collect the 00 UTC runs of ``source`` from ``start`` to ``end`` (selected months) into the archive.

    Resumable: units whose manifest is already complete are skipped; partial or
    missing ones are collected again. Writes into data/forecasts/<source>/<AAAA>/<MM>/.
    """
    adapter = adapters.ADAPTERS[source.family]
    restricted = restrict_to_max_step(source, max_step)
    result = BackfillResult()
    t0 = clock()
    day = start
    while day <= end:
        if day.month in months:
            if max_hours is not None and clock() - t0 >= max_hours * 3600:
                result.stopped = True
                break
            ref = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
            unit = Unit(source.id, ref)
            target = Path(data_dir) / "forecasts" / source.id / f"{ref:%Y}" / f"{ref:%m}"
            manifest = target / f"{source.id}_{ref:%Y%m%dT%HZ}.json"
            previous = _existing(manifest) if manifest.exists() else None
            if retry_given_up and previous is not None and previous["state"] != "complete":
                previous = {**previous, "attempts": 0, "throttled_passes": 0}  # counts start afresh
            if previous is not None and previous["state"] == "complete":
                result.skipped += 1
            elif previous is not None and (previous.get("attempts", 1) >= MAX_ATTEMPTS
                                           or previous.get("throttled_passes", 0) >= MAX_THROTTLED_PASSES):
                result.given_up += 1
            else:
                uid = unit_id(unit, "forecast")
                # Progress for the log of the pilot's PC: a unit can take minutes when AWS throttles.
                print(f"{uid}: collecting", flush=True)
                exhausted, requests_before, retries_before, t_unit = (
                    http.exhausted_count, http.request_count, http.retry_count, clock())
                m = adapter.collect(unit, restricted, http, target, "backfill", settings)
                attempts = previous.get("attempts", 1) if previous else 0
                throttled_passes = previous.get("throttled_passes", 0) if previous else 0
                throttled = m.state != "complete" and http.exhausted_count > exhausted
                if throttled:
                    throttled_passes += 1
                else:
                    attempts += 1
                if manifest.exists():
                    data = json.loads(manifest.read_text(encoding="utf-8"))
                    data["attempts"] = attempts
                    data["throttled_passes"] = throttled_passes
                    if throttled:
                        data.setdefault("notes", []).append(
                            "partial because the server throttled (retries exhausted): retried, not counted as an attempt")
                    if m.state != "complete" and (attempts >= MAX_ATTEMPTS or throttled_passes >= MAX_THROTTLED_PASSES):
                        data.setdefault("notes", []).append(
                            f"given up after {attempts} attempts and {throttled_passes} throttled passes")
                    manifest.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
                result.done += 1
                result.partial += m.state != "complete"
                print(f"{uid}: {m.state} in {clock() - t_unit:.0f} s, {http.request_count - requests_before} requests, "
                      f"{http.retry_count - retries_before} retries" + (f" ({m.notes[0]})" if m.notes else ""), flush=True)
        day += timedelta(days=1)
    return result


def default_range(source: Source, settings: dict, now: datetime) -> tuple[date, date]:
    """Backfill period of ``source`` from the catalogue; no end means the last published day."""
    b = settings["backfill"]
    last = last_available_day(source, now)
    end = b.get("end", {}).get(source.id)
    return b["start"][source.id], last if end is None else min(end, last)


@dataclass(frozen=True)
class Progress:
    expected: int  # 00 UTC runs of the selected months in the period
    complete: int
    incomplete: int  # partial or missing, still retried
    given_up: int  # partial or missing, no longer retried
    given_up_units: tuple = ()  # (unit id, missing pairs, first note) of each given-up unit


def progress(source: Source, start: date, end: date, data_dir: Path, months: tuple[int, ...]) -> Progress:
    """Count the backfill units of ``source`` already in the archive (manifest states, no checksum)."""
    expected = complete = incomplete = given_up = 0
    details = []
    day = start
    while day <= end:
        if day.month in months:
            expected += 1
            path = (Path(data_dir) / "forecasts" / source.id / f"{day:%Y}" / f"{day:%m}"
                    / f"{source.id}_{day:%Y%m%d}T00Z.json")
            try:
                m = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                m = None
            if m is not None and m.get("state") == "complete":
                complete += 1
            elif m is not None and (int(m.get("attempts", 1)) >= MAX_ATTEMPTS
                                    or int(m.get("throttled_passes", 0)) >= MAX_THROTTLED_PASSES):
                given_up += 1
                notes = [n for n in m.get("notes", []) if not n.startswith("given up")]
                details.append((m.get("unit", path.stem), len(m.get("missing", [])), notes[0] if notes else ""))
            elif m is not None:
                incomplete += 1
        day += timedelta(days=1)
    return Progress(expected, complete, incomplete, given_up, tuple(details))


def render_progress(source_id: str, p: Progress, width: int = 30) -> str:
    """One text line: ``source [#####-----] done/expected percent``."""
    share = p.complete / p.expected if p.expected else 1.0
    filled = round(width * share)
    line = f"{source_id:<12} [{'#' * filled}{'-' * (width - filled)}] {p.complete:>4}/{p.expected:<4} {100 * share:>3.0f} %"
    if p.given_up:
        line += f", {p.given_up} given up"
    if p.complete == p.expected:
        line += "  finished"
    for unit, missing, note in p.given_up_units:
        line += f"\n  given up: {unit}, {missing} missing" + (f" ({note})" if note else "")
    return line
