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

import requests

from powatlas.units import parse_artifact_name, parse_unit_id
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
    ids = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            ids.add(json.loads(line)["artifact_id"])
        except (ValueError, KeyError):
            # A line cut by a crash while appending: its artifact is synced again.
            print(f"ignored unreadable inventory line: {line[:80]!r}")
    return ids


def _from_collect_on_main(artifact: dict) -> bool:
    """Only artifacts of runs on main of this repository (never from a fork or a branch)."""
    run = artifact.get("workflow_run") or {}
    return run.get("head_branch") == "main" and run.get("head_repository_id") == run.get("repository_id") is not None


def target_dir(data_dir: Path, source: str, ref: datetime, kind: str) -> Path:
    top = "forecasts" if kind == "forecast" else "observations"
    return data_dir / top / source / f"{ref:%Y}" / f"{ref:%m}"


def _extract_and_verify(content: bytes, workdir: Path) -> dict:
    """Extract an artifact zip and check every file against its manifest; return the manifest."""
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        for name in z.namelist():
            if "/" in name or "\\" in name or name.startswith("."):
                raise ValueError(f"unexpected path in artifact: {name}")
        z.extractall(workdir)
    return verify_unit_dir(workdir)


def verify_unit_dir(workdir: Path) -> dict:
    """Check every file of a unit folder against its single manifest; return the manifest."""
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


def store_unit(data_dir: Path, workdir: Path, manifest: dict) -> str:
    """Move a verified unit folder into the archive: "new", "replaced", or "kept" when the
    archive already holds a better (or equally good) unit. Raises OSError if a move fails."""
    unit = parse_unit_id(manifest["unit"])
    kind = "forecast" if "T" in manifest["unit"].split("__")[1] else "observation"
    target = target_dir(data_dir, unit.source, unit.ref, kind)
    existing_path = target / manifest["_manifest_name"]
    state = manifest["state"]
    outcome = "new"
    existing = None
    if existing_path.exists():
        existing = json.loads(existing_path.read_text(encoding="utf-8"))
        worse = (_RANK[state], -len(manifest.get("missing", []))) < (
            _RANK[existing["state"]], -len(existing.get("missing", [])))
        outcome = "kept" if worse else "replaced"
    if outcome == "kept":
        return outcome
    # New files first, then the manifest, then the leftovers of the old unit:
    # an interruption leaves at worst extra files, never a manifest without files.
    target.mkdir(parents=True, exist_ok=True)
    for f in manifest["files"]:
        os.replace(workdir / f["name"], target / f["name"])
    os.replace(workdir / manifest["_manifest_name"], existing_path)
    if existing is not None:
        keep = {f["name"] for f in manifest["files"]}
        for f in existing["files"]:
            if f["name"] not in keep:
                try:
                    (target / f["name"]).unlink(missing_ok=True)
                except OSError as exc:
                    print(f"could not remove old file {f['name']}: {exc}")
    return outcome


def sync(data_dir: Path, gh, now: datetime) -> SyncResult:
    data_dir = Path(data_dir)
    result = SyncResult()
    artifacts = []
    for a in gh.list_artifacts():
        parsed = parse_artifact_name(a["name"])
        if parsed is None or not _from_collect_on_main(a):
            continue
        created = datetime.strptime(a["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        artifacts.append((created, a["id"], a["name"], parsed))
    if artifacts:
        result.stale_hours = (now - max(c for c, *_ in artifacts)).total_seconds() / 3600
    done = _synced_ids(data_dir)
    for created, aid, name, (unit, state) in sorted(artifacts):
        if aid in done:
            continue
        tmp_root = data_dir / ".tmp"
        tmp_root.mkdir(parents=True, exist_ok=True)
        workdir = Path(tempfile.mkdtemp(dir=tmp_root))
        try:
            try:
                manifest = _extract_and_verify(gh.download_artifact(aid), workdir)
                if manifest["unit"] != name.rsplit("__", 1)[0] or manifest["state"] != state:
                    raise ValueError(f"manifest {manifest['unit']} {manifest['state']} does not match the artifact name")
            except (zipfile.BadZipFile, ValueError, KeyError, OSError, RuntimeError, requests.RequestException) as exc:
                result.rejected.append(name)
                print(f"rejected {name}: {exc}")
                continue
            try:
                outcome = store_unit(data_dir, workdir, manifest)
            except OSError as exc:
                result.rejected.append(name)
                print(f"rejected {name} (retried next time): {exc}")
                continue
            setattr(result, outcome, getattr(result, outcome) + 1)
            _inventory(data_dir).parent.mkdir(parents=True, exist_ok=True)
            with open(_inventory(data_dir), "a", encoding="utf-8") as inv:
                inv.write(json.dumps({"artifact_id": aid, "name": name, "unit": manifest["unit"], "state": state,
                                      "outcome": outcome, "artifact_created": f"{created:%Y-%m-%dT%H:%M:%SZ}",
                                      "synced_at": f"{now:%Y-%m-%dT%H:%M:%SZ}"}) + "\n")
        finally:
            shutil.rmtree(workdir, ignore_errors=True)
    return result
