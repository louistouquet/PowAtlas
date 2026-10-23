#!/usr/bin/env python3
"""Print the reminders due for the pilot, read from docs/collecte/rappels.toml.

Usage: python3 scripts/reminders.py [--file PATH] [--today AAAA-MM-JJ]

Called by scripts/session-start.sh so that every Claude session starts with
them. Three kinds of entries: the last ``sync`` known on the pilot's PC
(artifacts stay 30 days on GitHub), dated deadlines, and actions waiting for
the pilot. Standard library only.
"""

from __future__ import annotations

import argparse
import tomllib
from datetime import date, datetime, timezone
from pathlib import Path

DEFAULT_FILE = Path(__file__).resolve().parent.parent / "docs" / "collecte" / "rappels.toml"


def reminders(conf: dict, today: date) -> list[str]:
    lines = []
    pc = conf.get("pc", {})
    if "last_sync" in pc:
        age = (today - pc["last_sync"]).days
        if age >= pc.get("warn_after_days", 20):
            lines.append(
                f"PC: last sync known {pc['last_sync']} ({age} days ago; artifacts are deleted after 30 days): "
                "ask the pilot to run `status` and check that the scheduled task runs"
            )
    for d in conf.get("deadline", []):
        if today > d["due"]:
            lines.append(f"OVERDUE since {d['due']}: {d['what']}")
        elif (d["due"] - today).days <= d.get("warn_days", 30):
            lines.append(f"Due {d['due']} (in {(d['due'] - today).days} days): {d['what']}")
    for w in conf.get("waiting", []):
        lines.append(f"Waiting for the pilot since {w['since']} ({(today - w['since']).days} days): {w['what']}")
    return lines


def render(path: Path, today: date) -> str:
    conf = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    lines = reminders(conf, today)
    if not lines:
        return "PowAtlas reminders: nothing due."
    return "PowAtlas reminders (tell the pilot, update docs/collecte/rappels.toml when done):\n" + "\n".join(
        f"- {line}" for line in lines
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE)
    parser.add_argument("--today", type=date.fromisoformat, default=datetime.now(timezone.utc).date())
    args = parser.parse_args()
    print(render(args.file, args.today))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
