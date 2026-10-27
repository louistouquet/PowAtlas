"""Observations collected on the pilot's PC (sources of task ``pc``), straight into the archive.

Some producers no longer answer data-centre networks (Arpa Piemonte since
2026-10-24, docs/collecte/suivi.md section 5): the daily job of the PC collects
them and files each unit as ``sync`` does, with the same rule (a worse unit never
replaces a better one). ``store_copies`` files the folders of manual copies
(``powatlas collect --out <folder>``).
"""

import gzip
import json
import re
import shutil
import tempfile
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from powatlas import adapters
from powatlas.catalogue import Source
from powatlas.http import HttpClient
from powatlas.sync import store_unit, target_dir, verify_unit_dir
from powatlas.units import Unit, unit_id


@dataclass
class StoreResult:
    new: int = 0
    replaced: int = 0
    kept: int = 0  # the archive already held a unit at least as good: the copy is dropped
    rejected: list = field(default_factory=list)  # left in place


def store_copies(data_dir: Path, copies_dir: Path) -> StoreResult:
    """File every unit folder of ``copies_dir`` into the archive once its sha256 sums match."""
    result = StoreResult()
    if not Path(copies_dir).is_dir():
        return result
    for folder in sorted(p for p in Path(copies_dir).iterdir() if p.is_dir()):
        try:
            manifest = verify_unit_dir(folder)
            if manifest["unit"] != folder.name:
                raise ValueError(f"manifest unit {manifest['unit']} differs from the folder name")
            outcome = store_unit(Path(data_dir), folder, manifest)
        except (ValueError, KeyError, OSError) as exc:
            result.rejected.append(folder.name)
            print(f"rejected {folder.name} (left in place): {exc}")
            continue
        setattr(result, outcome, getattr(result, outcome) + 1)
        shutil.rmtree(folder, ignore_errors=True)
    return result


def _complete_in_archive(data_dir: Path, unit: Unit) -> bool:
    path = target_dir(data_dir, unit.source, unit.ref, "observation") / f"{unit.source}_{unit.ref:%Y%m%d}.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))["state"] == "complete"
    except (OSError, ValueError, KeyError):
        return False


def collect_pc(data_dir: Path, http: HttpClient, sources: dict[str, Source], settings: dict,
               now: datetime) -> list[tuple[str, str, str]]:
    """Collect today's unit of each observation source of task ``pc`` into the archive.

    Today's unit whatever the hour: every copy covers several days (7 for Arpa), so a
    copy made before ``available_after_hours`` loses nothing. Returns (unit id, state,
    outcome) per source; outcome is "already complete" when nothing was fetched.
    """
    data_dir = Path(data_dir)
    day = now.astimezone(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    results = []
    for source in sources.values():
        if source.task != "pc" or source.kind != "observation":
            continue
        unit = Unit(source.id, day)
        uid = unit_id(unit, "observation")
        if _complete_in_archive(data_dir, unit):
            results.append((uid, "complete", "already complete"))
            continue
        tmp_root = data_dir / ".tmp"
        tmp_root.mkdir(parents=True, exist_ok=True)
        workdir = Path(tempfile.mkdtemp(dir=tmp_root))
        try:
            m = adapters.ADAPTERS[source.family].collect(unit, source, http, workdir, "daily", settings)
            outcome = store_unit(data_dir, workdir, verify_unit_dir(workdir))
            results.append((uid, m.state, outcome))
        finally:
            shutil.rmtree(workdir, ignore_errors=True)
    return results


_DAY = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:$|[T ])")


def dates_in_payload(content: bytes) -> dict[str, int]:
    """Count the days (AAAA-MM-JJ) that start the string values of a JSON payload, gzip or not:
    shows which days an archived observation copy covers."""
    if content[:2] == b"\x1f\x8b":
        content = gzip.decompress(content)
    counts: Counter = Counter()

    def walk(value) -> None:
        if isinstance(value, dict):
            for v in value.values():
                walk(v)
        elif isinstance(value, list):
            for v in value:
                walk(v)
        elif isinstance(value, str) and (m := _DAY.match(value)):
            counts[m[1]] += 1

    walk(json.loads(content))
    return dict(sorted(counts.items()))
