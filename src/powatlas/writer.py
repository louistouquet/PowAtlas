"""Writing of archive units (NetCDF for forecasts, raw gzip for observations) and manifests.

Every file written is described by a manifest (JSON next to it) giving its
sha256, the producer's Last-Modified of every file read (availability time,
needed by the no-leakage rule of SP3), and what is missing.
"""

import gzip
import hashlib
import json
import os
import re
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import netCDF4
import numpy as np

from powatlas import __version__
from powatlas.catalogue import Source, expected_pairs
from powatlas.grib import Field
from powatlas.units import Unit, unit_id

MODES = ("daily", "catchup", "backfill")
NETCDF_COMPRESSION = {"zlib": True, "complevel": 4, "shuffle": True}
# Query parameters of signed links (S3, Azure, generic tokens): never archived.
_SIGNED = re.compile(
    r"[?&](X-Amz-Signature|X-Amz-Credential|X-Amz-Security-Token|X-Goog-Signature|X-Goog-Credential"
    r"|Signature|Key-Pair-Id|Policy|sig|token|access_token|apikey|api_key)=",
    re.I,
)
# GRIB keys that must not change from one step to another within a variable.
IDENTITY_KEYS = ("shortName", "paramId", "typeOfLevel", "level", "stepType")


@dataclass(frozen=True)
class Fetched:
    url: str
    last_modified: datetime | None
    size: int
    rejected: bool = False  # read but not archived (e.g. previous day's run still on the server)


@dataclass
class Manifest:
    unit: str
    source: str
    ref: str
    state: str
    mode: str
    stream: str | None
    files: list = field(default_factory=list)
    fetched: list = field(default_factory=list)
    collected_start: str = ""
    collected_end: str = ""
    last_modified_min: str | None = None
    last_modified_max: str | None = None
    missing: list = field(default_factory=list)
    nan_counts: dict = field(default_factory=dict)  # "variable@step" -> NaN points in the cropped field
    notes: list = field(default_factory=list)
    fiche: str = ""
    licence: str = ""
    attribution: str = ""
    powatlas_version: str = __version__
    git_commit: str = ""


def _iso(t: datetime | None) -> str | None:
    if t is None:
        return None
    return t.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def git_commit() -> str:
    """Commit of the running code: GITHUB_SHA on Actions, else the local checkout, else 'unknown'."""
    if os.environ.get("GITHUB_SHA"):
        return os.environ["GITHUB_SHA"]
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=Path(__file__).parent, capture_output=True, text=True, check=True
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return out.stdout.strip()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _check_urls(fetched: list[Fetched]) -> None:
    for f in fetched:
        if _SIGNED.search(f.url):
            raise ValueError(f"signed link must not be archived: {f.url.split('?')[0]}?...")


def _base_manifest(unit: Unit, source: Source, mode: str, stream, fetched, collected_start) -> Manifest:
    if mode not in MODES:
        raise ValueError(f"unknown mode {mode}")
    _check_urls(fetched)
    kept = [f for f in fetched if not f.rejected]
    times = [f.last_modified for f in kept if f.last_modified is not None]
    complete_times = len(times) == len(kept)
    m = Manifest(
        unit=unit_id(unit, source.kind),
        source=source.id,
        ref=_iso(unit.ref),
        state="missing",
        mode=mode,
        stream=stream,
        fetched=[
            {"url": f.url, "last_modified": _iso(f.last_modified), "size": f.size, "rejected": f.rejected}
            for f in fetched
        ],
        collected_start=_iso(collected_start),
        last_modified_min=_iso(min(times)) if times else None,
        # The availability of the unit is unknown if any file lacks a Last-Modified.
        last_modified_max=_iso(max(times)) if times and complete_times else None,
        fiche=source.fiche,
        licence=source.licence,
        attribution=source.attribution,
        git_commit=git_commit(),
    )
    if not complete_times:
        m.notes.append(f"Last-Modified absent for {len(kept) - len(times)} of {len(kept)} files")
    return m


def _write_manifest(out_dir: Path, stem: str, m: Manifest) -> Manifest:
    m.collected_end = _iso(_now())
    tmp = out_dir / f".{stem}.json.tmp"
    tmp.write_text(json.dumps(asdict(m), indent=1, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, out_dir / f"{stem}.json")
    return m


def read_manifest(path: Path) -> Manifest:
    return Manifest(**json.loads(Path(path).read_text(encoding="utf-8")))


def write_forecast_unit(
    out_dir: Path,
    unit: Unit,
    source: Source,
    fields: dict[tuple[str, int], Field],
    expected: list[tuple[str, int]],
    fetched: list[Fetched],
    mode: str,
    stream: str | None,
    collected_start: datetime,
    notes: list[str] | None = None,
) -> Manifest:
    """Write one forecast unit as ``<source>_<AAAAMMJJTHHZ>.nc`` plus its manifest.

    ``fields`` maps (variable id, step in hours) to an already cropped Field.
    State: complete if every expected pair is present, partial if some are,
    missing if none (no NetCDF file is written then).
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{source.id}_{unit.ref.strftime('%Y%m%dT%HZ')}"
    m = _base_manifest(unit, source, mode, stream, fetched, collected_start)
    m.notes += list(notes or [])
    catalogue_pairs = expected_pairs(source)
    outside = sorted(set(expected) - set(catalogue_pairs))
    if outside:
        raise ValueError(f"expected pairs not in the catalogue of {source.id}: {outside}")
    # Only a backfill may expect less than the catalogue (fields not yet published then).
    if mode != "backfill" and set(expected) != set(catalogue_pairs):
        raise ValueError(f"{source.id}: expected pairs differ from the catalogue outside backfill")
    unexpected = set(fields) - set(expected)
    if unexpected:
        raise ValueError(f"fields not in the expected list: {sorted(unexpected)}")
    fields = dict(fields)
    for (var, step), f in list(fields.items()):
        if f.step_end != step:
            raise ValueError(f"{var}@{step}: field step is {f.step_end_minutes} min")
        n_nan = int(np.isnan(f.values).sum())
        m.nan_counts[f"{var}@{step}"] = n_nan
        if n_nan == f.values.size:
            m.notes.append(f"{var}@{step}: every point missing, counted as absent")
            del fields[(var, step)]
    for var in {v for v, _ in fields}:
        ids = {tuple(f.keys.get(k) for k in IDENTITY_KEYS) for (v, _), f in fields.items() if v == var}
        if len(ids) != 1:
            raise ValueError(f"{var}: GRIB identity {IDENTITY_KEYS} varies across steps: {sorted(ids)}")
    m.missing = [f"{v}@{s}" for v, s in expected if (v, s) not in fields]
    if not fields:
        return _write_manifest(out_dir, stem, m)

    first = next(iter(fields.values()))
    for key, f in fields.items():
        if f.values.shape != first.values.shape or not (
            np.array_equal(f.lats, first.lats) and np.array_equal(f.lons, first.lons)
        ):
            raise ValueError(f"{key}: cropped grid differs from the other fields of the unit")
        if f.ref_time != unit.ref:
            raise ValueError(f"{key}: run {f.ref_time} is not the unit run {unit.ref}")

    variables = list(dict.fromkeys(v for v, _ in expected))
    steps = sorted({s for _, s in expected})
    path = out_dir / f"{stem}.nc"
    tmp = out_dir / f".{stem}.nc.tmp"
    with netCDF4.Dataset(tmp, "w", format="NETCDF4") as ds:
        ds.createDimension("step", len(steps))
        ds.createDimension("lat", first.lats.size)
        ds.createDimension("lon", first.lons.size)
        vstep = ds.createVariable("step", "i4", ("step",))
        vstep[:] = steps
        vstep.units = "hours since reference_time"
        vlat = ds.createVariable("lat", "f8", ("lat",))
        vlat[:] = first.lats
        vlat.units = "degrees_north"
        vlon = ds.createVariable("lon", "f8", ("lon",))
        vlon[:] = first.lons
        vlon.units = "degrees_east"
        for var in variables:
            present = [(s, fields[(var, s)]) for s in steps if (var, s) in fields]
            nc = ds.createVariable(var, "f4", ("step", "lat", "lon"), fill_value=np.float32(np.nan),
                                   **NETCDF_COMPRESSION)
            data = np.full((len(steps), first.lats.size, first.lons.size), np.nan, dtype=np.float32)
            for s, f in present:
                data[steps.index(s)] = f.values
            nc[:] = data
            if present:
                for k, val in present[0][1].keys.items():
                    if k != "stepRange":
                        setattr(nc, f"GRIB_{k}", val)
                nc.GRIB_stepRange_by_step = json.dumps({str(s): f.keys.get("stepRange") for s, f in present})
        ds.source_id = source.id
        ds.fiche = source.fiche
        ds.licence = source.licence
        ds.attribution = source.attribution
        ds.reference_time = _iso(unit.ref)
        ds.mode = mode
        ds.stream = stream or ""
        ds.powatlas_version = __version__
        ds.git_commit = m.git_commit
        ds.fetched = json.dumps(m.fetched)
        ds.history = f"{_iso(_now())} written by powatlas {__version__}: cropped, values as published"
    os.replace(tmp, path)
    m.files = [{"name": path.name, "sha256": sha256_file(path), "size": path.stat().st_size}]
    m.state = "complete" if not m.missing else "partial"
    return _write_manifest(out_dir, stem, m)


def write_observation_unit(
    out_dir: Path,
    unit: Unit,
    source: Source,
    payloads: list[tuple[str, bytes, Fetched]],
    expected: list[str],
    mode: str,
    collected_start: datetime,
    notes: list[str] | None = None,
) -> Manifest:
    """Write raw responses verbatim (gzip) as ``<source>_<AAAAMMJJTHHMMZ>_<name>.gz`` plus a manifest."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = collected_start.astimezone(timezone.utc).strftime("%Y%m%dT%H%MZ")
    stem = f"{source.id}_{unit.ref.strftime('%Y%m%d')}"
    m = _base_manifest(unit, source, mode, None, [p[2] for p in payloads], collected_start)
    m.notes += list(notes or [])
    names = [p[0] for p in payloads]
    if len(set(names)) != len(names) or set(names) - set(expected):
        raise ValueError(f"payload names {names} do not match expected {expected}")
    for name, content, _ in payloads:
        already_gzip = content[:2] == b"\x1f\x8b"
        path = out_dir / f"{source.id}_{stamp}_{name}{'' if already_gzip else '.gz'}"
        tmp = out_dir / f".{path.name}.tmp"
        # Already gzip-compressed files are kept byte for byte; mtime=0 otherwise,
        # so that the gzip bytes depend only on the content.
        tmp.write_bytes(content if already_gzip else gzip.compress(content, mtime=0))
        os.replace(tmp, path)
        m.files.append({"name": path.name, "sha256": sha256_file(path), "size": path.stat().st_size})
    m.missing = [n for n in expected if n not in names]
    m.state = "missing" if not payloads else ("complete" if not m.missing else "partial")
    return _write_manifest(out_dir, stem, m)
