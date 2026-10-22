"""Loading of the declarative source catalogue (``catalogue.toml``)."""

import tomllib
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Literal

from powatlas.grib import GridSpec

Attempt = Literal["first", "last"]


@dataclass(frozen=True)
class Source:
    id: str
    family: str
    kind: Literal["forecast", "observation"]
    task: str
    fiche: str
    licence: str
    attribution: str
    run_hours: tuple[int, ...]
    steps: tuple[int, ...]
    variables: dict
    grid: GridSpec | None
    window_days: int
    available_after_hours: float
    urls: dict


@dataclass(frozen=True)
class Task:
    id: str
    crons: tuple[str, str]  # first trigger, then second (last) trigger


def expand_steps(ranges: list[list[int]]) -> tuple[int, ...]:
    """Expand inclusive [start, stop, step] ranges; ranges must not overlap."""
    steps: list[int] = []
    for start, stop, step in ranges:
        if step <= 0 or stop < start:
            raise ValueError(f"bad step range {[start, stop, step]}")
        part = list(range(start, stop + 1, step))
        if steps and part[0] <= steps[-1]:
            raise ValueError(f"step range {[start, stop, step]} overlaps the previous one")
        steps.extend(part)
    return tuple(steps)


def _source(sid: str, raw: dict) -> Source:
    if raw["kind"] not in ("forecast", "observation"):
        raise ValueError(f"{sid}: unknown kind {raw['kind']}")
    grid = GridSpec(**raw["grid"]) if "grid" in raw else None
    return Source(
        id=sid,
        family=raw["family"],
        kind=raw["kind"],
        task=raw["task"],
        fiche=raw["fiche"],
        licence=raw["licence"],
        attribution=raw["attribution"],
        run_hours=tuple(raw.get("run_hours", [0])),
        steps=expand_steps(raw["steps"]) if "steps" in raw else (),
        variables=dict(raw["variables"]),
        grid=grid,
        window_days=int(raw["window_days"]),
        available_after_hours=float(raw["available_after_hours"]),
        urls=dict(raw["urls"]),
    )


def load_catalogue(path: Path | None = None) -> tuple[dict[str, Source], dict[str, Task], dict]:
    """Return (sources, tasks, settings) from the packaged catalogue or ``path``."""
    if path is None:
        text = resources.files("powatlas").joinpath("catalogue.toml").read_text(encoding="utf-8")
    else:
        text = Path(path).read_text(encoding="utf-8")
    raw = tomllib.loads(text)
    tasks = {}
    for tid, t in raw["tasks"].items():
        crons = tuple(t["crons"])
        if len(crons) != 2:
            raise ValueError(f"task {tid}: exactly two crons expected")
        tasks[tid] = Task(id=tid, crons=crons)
    sources = {sid: _source(sid, s) for sid, s in raw["sources"].items()}
    for s in sources.values():
        if s.task not in tasks:
            raise ValueError(f"source {s.id}: unknown task {s.task}")
    return sources, tasks, raw["settings"]


def task_for_cron(cron: str, tasks: dict[str, Task]) -> tuple[str, Attempt]:
    for t in tasks.values():
        if cron == t.crons[0]:
            return t.id, "first"
        if cron == t.crons[1]:
            return t.id, "last"
    raise KeyError(f"no task for cron {cron!r}")
