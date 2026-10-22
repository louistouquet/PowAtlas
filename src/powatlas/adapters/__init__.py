"""Registry of source adapters, indexed by ``Source.family``.

An adapter collects one unit and returns its manifest::

    collect(unit, source, http, out_dir, mode, settings) -> Manifest
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Protocol

from powatlas.catalogue import Source
from powatlas.http import HttpClient
from powatlas.units import Unit
from powatlas.writer import Manifest


class Adapter(Protocol):
    def collect(
        self, unit: Unit, source: Source, http: HttpClient, out_dir: Path, mode: str, settings: dict
    ) -> Manifest: ...


ADAPTERS: dict[str, Adapter] = {}


def out_of_time(start: datetime, settings: dict) -> bool:
    """True once the collection budget is spent: the unit is then written as it stands
    (partial, with a note) instead of the job being killed by its timeout without a manifest."""
    return datetime.now(timezone.utc) - start >= timedelta(minutes=settings["collect_budget_minutes"])


def accumulation_from_run_start(keys: dict) -> bool:
    """Accumulated fields of ICON, Météo-France and ECMWF start at the run time (step range 0-N)."""
    if keys.get("stepType") != "accum":
        return True
    step_range = str(keys.get("stepRange", ""))
    # At step 0 eccodes writes the empty 0-0 period as "0".
    return step_range in ("0", "0m") or step_range.startswith(("0-", "0m-"))
