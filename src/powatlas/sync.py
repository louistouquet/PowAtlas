"""Bringing workflow artifacts into the reference archive on the pilot's PC.

Nothing reaches ``data/`` before every file of the artifact has matched the
sha256 of its manifest; files are then moved with ``os.replace``. An artifact
that fails is not recorded, so it is retried at the next run.
"""

import io
import json
import os
import shutil
import tempfile
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from powatlas.units import parse_artifact_name
from powatlas.writer import sha256_file

_RANK = {"complete": 2, "partial": 1, "missing": 0}
STALE_WARNING_HOURS = 48


@dataclass
class SyncResult:
    new: int = 0
    replaced: int = 0
    kept: int = 0  # artifacts not better than what the archive already holds
    rejected: list = field(default_factory=list)
    stale_hours: float = float("inf")  # age of the newest artifact


def _inventory(data_dir: Path) -> Path:
    return data_dir / "journal" / "inventaire.jsonl"


def _synced_ids(data_dir: Path) -> set[int]:
    path = _inventory(data_dir)
    if not path.exists():
        return set()
    return {json.loads(line)["artifact_id"] for line in path.read_text(encoding="utf-8").splitlines() if line}


def _target_dir(data_dir: Path, source: str, ref: datetime, kind: str) -> Path:
    top = "forecasts" if kind == "forecast" else "observations"
    return data_dir / top / source / f"{ref:%Y}" / f"{ref:%m}"


def _extract_and_verify(content: bytes, workdir: Path) -> dict:
    """Extract an artifact zip and check every file against its manifest; return the manifest."""
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        for name in z.namelist():
            if "/" in name or "\\" in name or name.startswith("."):
                raise ValueError(f"unexpected path in artifact: {name}")
        z.extractall(workdir)
    manifests = [p for p in workdir.glob("*.json")]
    if len(manifests) != 1:
        raise ValueError(f"{len(manifests)} manifests in artifact")
    manifest = json.loads(manifests[0].read_text(encoding="utf-8"))
    listed = {f["name"] for f in manifest["files"]}
    present = {p.name for p in workdir.iterdir()} - {manifests[0].name}
    if listed != present:
        raise ValueError(f"files {sorted(present)} differ from manifest {sorted(listed)}")
    for f in manifest["files"]:
        if sha256_file(workdir / f["name"]) != f["sha256"]:
            raise ValueError(f"sha256 mismatch for {f['name']}")
    manifest["_manifest_name"] = manifests[0].name
    return manifest


def sync(data_dir: Path, gh, now: datetime) -> SyncResult:
    data_dir = Path(data_dir)
    result = SyncResult()
    artifacts = []
    for a in gh.list_artifacts():
        parsed = parse_artifact_name(a["name"])
        if parsed is None:
            continue
        created = datetime.strptime(a["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        artifacts.append((created, a["id"], a["name"], parsed))
    if artifacts:
        result.stale_hours = (now - max(c for c, *_ in artifacts)).total_seconds() / 3600
    done = _synced_ids(data_dir)
    for created, aid, name, (unit, state) in sorted(artifacts):
        if aid in done:
            continue
        kind = "forecast" if "T" in name.split("__")[1] else "observation"
        tmp_root = data_dir / ".tmp"
        tmp_root.mkdir(parents=True, exist_ok=True)
        workdir = Path(tempfile.mkdtemp(dir=tmp_root))
        try:
            try:
                manifest = _extract_and_verify(gh.download_artifact(aid), workdir)
            except (zipfile.BadZipFile, ValueError, KeyError, OSError) as exc:
                result.rejected.append(name)
                print(f"rejected {name}: {exc}")
                continue
            target = _target_dir(data_dir, unit.source, unit.ref, kind)
            existing_path = target / manifest["_manifest_name"]
            outcome = "new"
            if existing_path.exists():
                existing = json.loads(existing_path.read_text(encoding="utf-8"))
                if _RANK[state] < _RANK[existing["state"]]:
                    outcome = "kept"
                else:
                    outcome = "replaced"
                    for f in existing["files"]:
                        (target / f["name"]).unlink(missing_ok=True)
            if outcome != "kept":
                target.mkdir(parents=True, exist_ok=True)
                for f in manifest["files"]:
                    os.replace(workdir / f["name"], target / f["name"])
                os.replace(workdir / manifest["_manifest_name"], existing_path)
            setattr(result, outcome, getattr(result, outcome) + 1)
            _inventory(data_dir).parent.mkdir(parents=True, exist_ok=True)
            with open(_inventory(data_dir), "a", encoding="utf-8") as inv:
                inv.write(json.dumps({"artifact_id": aid, "name": name, "unit": manifest["unit"], "state": state,
                                      "outcome": outcome, "artifact_created": f"{created:%Y-%m-%dT%H:%M:%SZ}",
                                      "synced_at": f"{now:%Y-%m-%dT%H:%M:%SZ}"}) + "\n")
        finally:
            shutil.rmtree(workdir, ignore_errors=True)
    return result
