"""Dated verbatim copies of observation APIs and files (SLF, Arpa Piemonte, Météo-France).

Nothing is parsed into values in SP1: answers are stored as received, with the
collection time, so that later scores know what was published when.
"""

import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

from powatlas.adapters import ADAPTERS
from powatlas.catalogue import Source
from powatlas.http import HttpClient, HttpError, NotFound
from powatlas.units import Unit
from powatlas.writer import Fetched, Manifest, write_observation_unit

NEW_YEAR_DAYS = 7  # days of January during which last year's file is still copied
_SEASON = re.compile(r"Q_\d{2}_latest-(\d{4}-\d{4})_autres-parametres\.csv\.gz")


@dataclass(frozen=True)
class Item:
    name: str
    url: str
    optional: bool  # a 404 is not a missing item (new year's file not created yet)


def _seasons(listing_url: str, http: HttpClient) -> list[str]:
    seasons = sorted(set(_SEASON.findall(http.get(listing_url).content.decode("utf-8"))))
    if not seasons:
        raise ValueError(f"no 'latest' season found in {listing_url}")
    return seasons


def snapshot_items(source: Source, day: date, http: HttpClient) -> list[Item]:
    items: list[Item] = []
    for name, spec in source.variables.items():
        rule = spec.get("rule")
        if rule is None:
            items.append(Item(name, spec["url"], optional=False))
        elif rule == "yearly":
            new_year = day.month == 1 and day.day <= NEW_YEAR_DAYS
            if new_year:
                y = day.year - 1
                items.append(Item(spec["name"].format(year=y), spec["url"].format(year=y), optional=False))
            items.append(Item(spec["name"].format(year=day.year), spec["url"].format(year=day.year), optional=new_year))
        elif rule == "quot":
            for season in _seasons(spec["listing"], http):
                for dep in spec["departments"]:
                    fmt = {"dep": dep, "season": season}
                    items.append(Item(spec["name"].format(**fmt), spec["url"].format(**fmt), optional=False))
        else:
            raise ValueError(f"{source.id}/{name}: unknown rule {rule}")
    return items


def _problem(name: str, content: bytes) -> str | None:
    """Why a 200 answer is not usable, or None."""
    if not content:
        return "empty answer"
    if name.endswith(".json"):
        obj = json.loads(content)
        if isinstance(obj, dict) and {"title", "status"} <= obj.keys():
            return f"error document: {obj.get('status')} {obj.get('title')}"
    return None


class SnapshotAdapter:
    def collect(
        self, unit: Unit, source: Source, http: HttpClient, out_dir: Path, mode: str, settings: dict
    ) -> Manifest:
        start = datetime.now(timezone.utc)
        items = snapshot_items(source, unit.ref.date(), http)
        payloads, notes, expected = [], [], []
        for item in items:
            try:
                r = http.get(item.url)
            except NotFound:
                if not item.optional:
                    expected.append(item.name)
                    notes.append(f"{item.name}: HTTP 404")
                continue
            except HttpError as exc:
                expected.append(item.name)
                notes.append(f"{item.name}: {exc}")
                continue
            expected.append(item.name)
            problem = _problem(item.name, r.content)
            if problem:
                notes.append(f"{item.name}: {problem}")
                continue
            payloads.append((item.name, r.content, Fetched(item.url, r.last_modified, len(r.content))))
        return write_observation_unit(out_dir, unit, source, payloads, expected, mode, start, notes)


ADAPTERS["snapshot"] = SnapshotAdapter()
