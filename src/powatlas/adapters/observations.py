"""Dated verbatim copies of observation APIs and files (SLF, Arpa Piemonte, Météo-France).

Nothing is parsed into values in SP1: answers are stored as received, with the
collection time and the kept response headers, so that later scores know what
was published when.
"""

import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np

from powatlas.adapters import ADAPTERS
from powatlas.catalogue import Source
from powatlas.domain import BBox, crop_points
from powatlas.http import HttpClient, HttpError, NotFound
from powatlas.units import Unit
from powatlas.writer import Fetched, Manifest, write_observation_unit

NEW_YEAR_DAYS = 7  # days of January during which last year's file is still copied
STATION_MARGIN_DEG = 0.1  # stations kept around the bbox
_SEASON = re.compile(r"Q_\d{2}_latest-(\d{4}-\d{4})_autres-parametres\.csv\.gz")


@dataclass(frozen=True)
class Item:
    name: str
    url: str
    optional: bool  # absent without being a loss (new year's file, station without sensor)
    no_data_status: tuple[int, ...] = ()  # HTTP statuses meaning "no data for this station"
    group: str | None = None  # per-station route the item belongs to


def _problem(name: str, content: bytes) -> str | None:
    """Why a 200 answer is not usable, or None."""
    if not content:
        return "empty answer"
    if name.endswith(".json"):
        try:
            obj = json.loads(content)
        except ValueError as exc:  # HTML error page, cut body
            return f"not JSON ({exc})"
        if isinstance(obj, dict) and {"title", "status"} <= obj.keys():
            return f"error document: {obj.get('status')} {obj.get('title')}"
    return None


def _station_codes(stations_url: str, http: HttpClient, bbox: BBox) -> list[str]:
    stations = json.loads(http.get(stations_url).content)
    lats = np.array([s["lat"] for s in stations], dtype=float)
    lons = np.array([s["lon"] for s in stations], dtype=float)
    return [stations[i]["code"] for i in crop_points(lats, lons, bbox, STATION_MARGIN_DEG)]


def snapshot_items(source: Source, day: date, http: HttpClient, settings: dict) -> tuple[list[Item], list[tuple[str, str]]]:
    """Items to copy for ``day``, and (name, reason) of the items that could not even be listed."""
    bbox = BBox(*settings["bbox"])
    items: list[Item] = []
    failures: list[tuple[str, str]] = []
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
            for dep in spec["departments"]:
                listing = spec["listing"].format(dep=dep)
                try:
                    seasons = sorted(set(_SEASON.findall(http.get(listing).content.decode("utf-8"))))
                except HttpError as exc:
                    failures.append((f"Q_{dep} listing", str(exc)))
                    continue
                if not seasons:
                    failures.append((f"Q_{dep} listing", "no 'latest' season in the bucket listing"))
                for season in seasons:
                    fmt = {"dep": dep, "season": season}
                    items.append(Item(spec["name"].format(**fmt), spec["url"].format(**fmt), optional=False))
        elif rule == "per-station":
            stations_url = source.variables[spec["stations"]]["url"]
            try:
                codes = _station_codes(stations_url, http, bbox)
            except (HttpError, ValueError, KeyError) as exc:
                failures.append((f"{name} (station list)", f"{type(exc).__name__}: {exc}"))
                continue
            for code in codes:
                items.append(Item(spec["name"].format(code=code), spec["url"].format(code=code), optional=False,
                                  no_data_status=tuple(spec["no_data_status"]), group=name))
        else:
            raise ValueError(f"{source.id}/{name}: unknown rule {rule}")
    return items, failures


class SnapshotAdapter:
    def collect(
        self, unit: Unit, source: Source, http: HttpClient, out_dir: Path, mode: str, settings: dict
    ) -> Manifest:
        start = datetime.now(timezone.utc)
        items, failures = snapshot_items(source, unit.ref.date(), http, settings)
        expected = [name for name, _ in failures]
        notes = [f"{name}: {why}" for name, why in failures]
        payloads = []
        no_data: dict[str, list[str]] = {}
        for item in items:
            try:
                r = http.get(item.url)
            except HttpError as exc:
                if exc.status in item.no_data_status:
                    no_data.setdefault(item.group, []).append(item.name)
                    continue
                if isinstance(exc, NotFound) and item.optional:
                    continue  # new year's file not created yet
                expected.append(item.name)
                notes.append(f"{item.name}: {exc}")
                continue
            expected.append(item.name)
            problem = _problem(item.name, r.content)
            if problem:
                notes.append(f"{item.name}: {problem}")
                continue
            if r.last_modified is not None and r.last_modified.date() < unit.ref.date():
                notes.append(f"{item.name}: not refreshed on the collection day (Last-Modified {r.last_modified:%Y-%m-%dT%H:%MZ})")
            payloads.append((item.name, r.content, Fetched(item.url, r.last_modified, len(r.content), headers=r.headers)))
        for group, names in no_data.items():
            total = sum(1 for i in items if i.group == group)
            codes = ", ".join(n.rsplit("_", 1)[1].removesuffix(".json") for n in names)
            notes.append(f"{group}: no data for {len(names)} of {total} stations ({codes})")
        return write_observation_unit(out_dir, unit, source, payloads, expected, mode, start, notes)


ADAPTERS["snapshot"] = SnapshotAdapter()
