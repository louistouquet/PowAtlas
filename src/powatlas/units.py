"""Units of collection and the artifact names that carry their state.

A unit is one source x one run (forecasts) or one source x one collection day
(observations). Its artifact is named ``<source>__<ref>__<state>`` where ref is
``AAAAMMJJTHHZ`` (forecasts) or ``AAAAMMJJ`` (observations).
"""

import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal

from powatlas.catalogue import Source

State = Literal["complete", "partial", "missing"]
STATES: tuple[State, ...] = ("complete", "partial", "missing")
_RANK = {"complete": 2, "partial": 1, "missing": 0}
_NAME = re.compile(r"^(?P<source>[a-z0-9-]+)__(?P<ref>\d{8}(T\d{2}Z)?)(__(?P<state>[a-z]+))?$")


@dataclass(frozen=True, order=True)
class Unit:
    source: str
    ref: datetime  # run time (forecasts) or collection day at 00 UTC (observations)

    def __post_init__(self) -> None:
        if self.ref.tzinfo is None or self.ref.utcoffset() != timedelta(0):
            raise ValueError(f"unit ref must be an aware UTC datetime, got {self.ref!r}")


def _ref_text(unit: Unit, kind: str) -> str:
    if kind == "forecast":
        return unit.ref.strftime("%Y%m%dT%HZ")
    if kind == "observation":
        return unit.ref.strftime("%Y%m%d")
    raise ValueError(f"unknown kind {kind}")


def unit_id(unit: Unit, kind: str) -> str:
    return f"{unit.source}__{_ref_text(unit, kind)}"


def artifact_name(unit: Unit, state: State, kind: str) -> str:
    if state not in STATES:
        raise ValueError(f"unknown state {state}")
    return f"{unit_id(unit, kind)}__{state}"


def _parse(text: str, with_state: bool):
    m = _NAME.match(text)
    if m is None or (m["state"] is None) == with_state:
        return None
    ref = m["ref"]
    fmt = "%Y%m%dT%HZ" if "T" in ref else "%Y%m%d"
    unit = Unit(m["source"], datetime.strptime(ref, fmt).replace(tzinfo=timezone.utc))
    if not with_state:
        return unit
    if m["state"] not in STATES:
        return None
    return unit, m["state"]


def parse_artifact_name(name: str) -> tuple[Unit, State] | None:
    """Unit and state of an artifact name; None for any other artifact."""
    return _parse(name, with_state=True)


def parse_unit_id(text: str) -> Unit:
    unit = _parse(text, with_state=False)
    if unit is None:
        raise ValueError(f"not a unit id: {text!r}")
    return unit


def best_states(artifact_names: Iterable[str]) -> dict[Unit, State]:
    """Best state seen per unit (complete > partial > missing)."""
    best: dict[Unit, State] = {}
    for name in artifact_names:
        parsed = parse_artifact_name(name)
        if parsed is None:
            continue
        unit, state = parsed
        if unit not in best or _RANK[state] > _RANK[best[unit]]:
            best[unit] = state
    return best


def expected_units(source: Source, now: datetime) -> list[Unit]:
    """Units of ``source`` that should exist at ``now`` within its catch-up window."""
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    today = now.astimezone(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    hours = source.run_hours if source.kind == "forecast" else (0,)
    units = []
    for back in range(source.window_days, -1, -1):
        day = today - timedelta(days=back)
        for h in hours:
            ref = day + timedelta(hours=h)
            if ref + timedelta(hours=source.available_after_hours) <= now:
                units.append(Unit(source.id, ref))
    return units


def units_to_collect(expected: list[Unit], artifact_names: Iterable[str]) -> list[Unit]:
    best = best_states(artifact_names)
    return [u for u in expected if best.get(u) != "complete"]


def definitive_losses(
    source: Source, now: datetime, attempt: str, artifact_names: Iterable[str]
) -> list[Unit]:
    """Units at the oldest edge of the window that are still not complete after the last trigger."""
    if attempt not in ("first", "last"):
        raise ValueError(f"unknown attempt {attempt}")
    if attempt == "first":
        return []
    expected = expected_units(source, now)
    if not expected:
        return []
    oldest_day = expected[0].ref.date()
    edge = [u for u in expected if u.ref.date() == oldest_day]
    return units_to_collect(edge, artifact_names)
