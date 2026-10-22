"""Planning, collection and reporting of a task (one GitHub Actions run)."""

from datetime import datetime
from pathlib import Path

from powatlas import adapters
from powatlas.catalogue import Source
from powatlas.http import HttpClient
from powatlas.units import best_states, definitive_losses, expected_units, parse_unit_id, unit_id, units_to_collect
from powatlas.writer import Manifest

INACTIVITY_WARNING_DAYS = 45  # GitHub disables scheduled workflows after 60 days without activity


def _task_sources(task: str, sources: dict[str, Source]) -> list[Source]:
    selected = [s for s in sources.values() if s.task == task]
    if not selected:
        raise KeyError(f"no source for task {task}")
    return selected


def plan(task: str, now: datetime, artifact_names: list[str], sources: dict[str, Source]) -> list[str]:
    """Unit ids of the task still to collect (absent or not complete within their window)."""
    ids = []
    for s in _task_sources(task, sources):
        ids += [unit_id(u, s.kind) for u in units_to_collect(expected_units(s, now), artifact_names)]
    return ids


def collect_unit(
    uid: str, out_dir: Path, http: HttpClient, sources: dict[str, Source], settings: dict, now: datetime
) -> Manifest:
    unit = parse_unit_id(uid)
    source = sources[unit.source]
    adapter = adapters.ADAPTERS[source.family]
    mode = "daily" if unit.ref.date() == now.date() else "catchup"
    return adapter.collect(unit, source, http, Path(out_dir) / uid, mode, settings)


def report(
    task: str,
    now: datetime,
    attempt: str,
    artifact_names: list[str],
    last_commit: datetime,
    sources: dict[str, Source],
) -> tuple[list[str], str]:
    """Definitive losses of the task and a Markdown summary of its window."""
    best = best_states(artifact_names)
    losses: list[str] = []
    lines = [f"## Collecte `{task}` ({attempt} trigger, {now:%Y-%m-%d %H:%M} UTC)", "",
             "| Unit | State |", "|---|---|"]
    for s in _task_sources(task, sources):
        for u in expected_units(s, now):
            lines.append(f"| `{unit_id(u, s.kind)}` | {best.get(u, 'not collected')} |")
        losses += [unit_id(u, s.kind) for u in definitive_losses(s, now, attempt, artifact_names)]
    if losses:
        lines += ["", "**Definitive losses:** " + ", ".join(f"`{x}`" for x in losses)]
    inactive_days = (now - last_commit).days
    if inactive_days >= INACTIVITY_WARNING_DAYS:
        lines += ["", f"**Repository inactive for {inactive_days} days**: scheduled workflows stop after 60 days "
                      "without activity. Commit real work (for example the monthly status update)."]
    return losses, "\n".join(lines) + "\n"
