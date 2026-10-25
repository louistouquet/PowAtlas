#!/usr/bin/env python3
"""Print the health of the daily collection on GitHub Actions (public API, no token).

Usage: python3 scripts/health.py

Called by scripts/session-start.sh so that every Claude session starts with it:
failed collect runs of the last 48 h, hours since the last successful run
(cron-job.org triggers one every hour), units of the last 3 days that are not
complete, and open issues labelled ``collecte``. The pilot's PC (sync, backfill)
is not visible from here: see docs/collecte/rappels.toml. Standard library only.
"""

from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timedelta, timezone

REPO = "louistouquet/PowAtlas"
API = f"https://api.github.com/repos/{REPO}"
FAILURE_WINDOW = timedelta(hours=48)
UNIT_WINDOW = timedelta(days=3)
MAX_SILENCE_HOURS = 2.0
_RANK = {"missing": 0, "partial": 1, "complete": 2}


def _time(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def health(runs: list[dict], artifacts: list[dict], issues: list[dict], now: datetime) -> list[str]:
    lines = []
    for r in runs:
        if r.get("conclusion") not in ("success", "skipped", None) and now - _time(r["created_at"]) <= FAILURE_WINDOW:
            lines.append(f"failed collect run {r['created_at']} ({r['event']}): "
                         f"https://github.com/{REPO}/actions/runs/{r['id']}")
    successes = [_time(r["created_at"]) for r in runs if r.get("conclusion") == "success"]
    if not successes:
        lines.append("no successful collect run in the listing")
    else:
        hours = (now - max(successes)).total_seconds() / 3600
        if hours > MAX_SILENCE_HOURS:
            lines.append(f"last successful collect run {hours:.1f} h ago (expected hourly, cron-job.org)")
    best: dict[str, str] = {}
    for a in artifacts:
        parts = a["name"].split("__")
        if a.get("expired") or len(parts) != 3 or parts[2] not in _RANK:
            continue
        if now - _time(a["created_at"]) > UNIT_WINDOW:
            continue
        unit = f"{parts[0]}__{parts[1]}"
        if unit not in best or _RANK[parts[2]] > _RANK[best[unit]]:
            best[unit] = parts[2]
    for unit in sorted(u for u, s in best.items() if s != "complete"):
        lines.append(f"unit not complete (retried while within its window): {unit} ({best[unit]})")
    for i in issues:
        lines.append(f"open issue {i['number']}: {i['title']} ({i['html_url']})")
    return lines


def render(lines: list[str]) -> str:
    if not lines:
        return "PowAtlas collection health: OK (GitHub side)."
    return "PowAtlas collection health (tell the pilot, investigate, fix):\n" + "\n".join(f"- {x}" for x in lines)


def _get(path: str):
    req = urllib.request.Request(API + path, headers={"Accept": "application/vnd.github+json",
                                                      "User-Agent": "PowAtlas-health"})
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.load(r)


def main() -> int:
    now = datetime.now(timezone.utc)
    try:
        runs = _get("/actions/workflows/collect.yml/runs?per_page=100")["workflow_runs"]
        artifacts = []
        for page in (1, 2, 3):
            artifacts += _get(f"/actions/artifacts?per_page=100&page={page}")["artifacts"]
        issues = [i for i in _get("/issues?labels=collecte&state=open") if "pull_request" not in i]
    except Exception as exc:  # the hook must never fail
        print(f"PowAtlas collection health: could not be checked ({type(exc).__name__}: {exc})")
        return 0
    print(render(health(runs, artifacts, issues, now)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
