"""Table of complete (C), partial (P), missing (M) and absent (-) units per source and day."""

import json
from datetime import date, timedelta
from pathlib import Path

from powatlas.catalogue import load_catalogue

_LETTER = {"complete": "C", "partial": "P", "missing": "M"}


def status(data_dir: Path, start: date, end: date) -> str:
    sources, _, _ = load_catalogue()
    seen: dict[tuple[str, date], str] = {}
    for top in ("forecasts", "observations"):
        for path in (Path(data_dir) / top).rglob("*.json"):
            m = json.loads(path.read_text(encoding="utf-8"))
            ref = m["unit"].split("__")[1]
            day = date(int(ref[:4]), int(ref[4:6]), int(ref[6:8]))
            seen[(m["source"], day)] = _LETTER[m["state"]]
    days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    lines = ["| Source | " + " | ".join(f"{d:%m-%d}" for d in days) + " |",
             "|---|" + "---|" * len(days)]
    for sid in sources:
        lines.append(f"| {sid} | " + " | ".join(seen.get((sid, d), "-") for d in days) + " |")
    return "\n".join(lines) + "\n"
