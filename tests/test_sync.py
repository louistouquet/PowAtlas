import io
import json
import tempfile
import unittest
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from powatlas.status import status
from powatlas.sync import sync
from powatlas.writer import sha256_file

NOW = datetime(2026, 11, 3, 12, tzinfo=timezone.utc)


def unit_zip(source, ref, state, files, kind="forecast", corrupt=False):
    """Zip of an artifact as written by the workflow: data files plus the manifest."""
    tmp = Path(tempfile.mkdtemp())
    entries = []
    for name, content in files.items():
        (tmp / name).write_bytes(content)
        entries.append({"name": name, "sha256": sha256_file(tmp / name), "size": len(content)})
    if corrupt:
        (tmp / list(files)[0]).write_bytes(b"tampered")
    stem = f"{source}_{ref}" if kind == "forecast" else f"{source}_{ref}"
    manifest = {"unit": f"{source}__{ref}", "source": source, "state": state, "files": entries}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name in files:
            z.write(tmp / name, name)
        z.writestr(f"{stem}.json", json.dumps(manifest))
    return buf.getvalue()


class FakeGitHub:
    def __init__(self, artifacts):
        self.artifacts = artifacts  # list of (id, name, created_at, zip bytes)
        self.downloads = []

    def list_artifacts(self):
        return [{"id": i, "name": n, "created_at": c.strftime("%Y-%m-%dT%H:%M:%SZ")} for i, n, c, _ in self.artifacts]

    def download_artifact(self, artifact_id):
        self.downloads.append(artifact_id)
        return next(z for i, _, _, z in self.artifacts if i == artifact_id)


def art(i, source, ref, state, files, hours_ago=1, **kw):
    return (i, f"{source}__{ref}__{state}", NOW - timedelta(hours=hours_ago), unit_zip(source, ref, state, files, **kw))


class SyncTest(unittest.TestCase):
    def setUp(self):
        self.data = Path(tempfile.mkdtemp())

    def test_sync_places_files_in_layout(self):
        gh = FakeGitHub([art(1, "icon-d2", "20261101T00Z", "complete", {"icon-d2_20261101T00Z.nc": b"nc"}),
                         art(2, "slf", "20261101", "complete", {"slf_20261101T0950Z_x.json.gz": b"gz"},
                             kind="observation")])
        r = sync(self.data, gh, NOW)
        self.assertEqual((r.new, r.replaced, r.rejected), (2, 0, []))
        self.assertTrue((self.data / "forecasts/icon-d2/2026/11/icon-d2_20261101T00Z.nc").is_file())
        self.assertTrue((self.data / "forecasts/icon-d2/2026/11/icon-d2_20261101T00Z.json").is_file())
        self.assertTrue((self.data / "observations/slf/2026/11/slf_20261101T0950Z_x.json.gz").is_file())
        lines = (self.data / "journal/inventaire.jsonl").read_text().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[0])["artifact_id"], 1)

    def test_already_synced_artifact_skipped(self):
        gh = FakeGitHub([art(1, "icon-d2", "20261101T00Z", "complete", {"icon-d2_20261101T00Z.nc": b"nc"})])
        sync(self.data, gh, NOW)
        r = sync(self.data, gh, NOW)
        self.assertEqual((r.new, gh.downloads), (0, [1]))

    def test_complete_replaces_partial(self):
        gh = FakeGitHub([art(1, "arome-0025", "20261101T00Z", "partial", {"arome-0025_20261101T00Z.nc": b"p"}, 30),
                         art(2, "arome-0025", "20261101T00Z", "complete", {"arome-0025_20261101T00Z.nc": b"c"}, 20)])
        r = sync(self.data, gh, NOW)
        self.assertEqual((r.new, r.replaced), (1, 1))
        self.assertEqual((self.data / "forecasts/arome-0025/2026/11/arome-0025_20261101T00Z.nc").read_bytes(), b"c")

    def test_partial_never_replaces_complete(self):
        gh = FakeGitHub([art(1, "arome-0025", "20261101T00Z", "complete", {"arome-0025_20261101T00Z.nc": b"c"}, 30),
                         art(2, "arome-0025", "20261101T00Z", "partial", {"arome-0025_20261101T00Z.nc": b"p"}, 20)])
        sync(self.data, gh, NOW)
        self.assertEqual((self.data / "forecasts/arome-0025/2026/11/arome-0025_20261101T00Z.nc").read_bytes(), b"c")

    def test_corrupt_artifact_leaves_archive_untouched(self):
        gh = FakeGitHub([art(1, "icon-d2", "20261101T00Z", "complete", {"icon-d2_20261101T00Z.nc": b"nc"}, corrupt=True),
                         (2, "icon-eu__20261101T00Z__complete", NOW, b"not a zip")])
        r = sync(self.data, gh, NOW)
        self.assertEqual(sorted(r.rejected), ["icon-d2__20261101T00Z__complete", "icon-eu__20261101T00Z__complete"])
        self.assertFalse((self.data / "forecasts").exists())
        self.assertFalse((self.data / "journal/inventaire.jsonl").exists())

    def test_stale_warning_after_48_hours(self):
        gh = FakeGitHub([art(1, "icon-d2", "20261101T00Z", "complete", {"icon-d2_20261101T00Z.nc": b"nc"}, 49)])
        r = sync(self.data, gh, NOW)
        self.assertGreater(r.stale_hours, 48)
        self.assertEqual(sync(self.data, FakeGitHub([]), NOW).stale_hours, float("inf"))

    def test_foreign_artifacts_ignored(self):
        r = sync(self.data, FakeGitHub([(9, "coverage-report", NOW, b"zip")]), NOW)
        self.assertEqual((r.new, r.rejected), (0, []))


class StatusTest(unittest.TestCase):
    def test_status_table(self):
        data = Path(tempfile.mkdtemp())
        gh = FakeGitHub([art(1, "icon-d2", "20261101T00Z", "complete", {"icon-d2_20261101T00Z.nc": b"nc"}),
                         art(2, "icon-d2", "20261102T00Z", "partial", {"icon-d2_20261102T00Z.nc": b"nc"})])
        sync(data, gh, NOW)
        table = status(data, datetime(2026, 11, 1).date(), datetime(2026, 11, 3).date())
        row = next(line for line in table.splitlines() if line.startswith("| icon-d2 "))
        self.assertEqual(row, "| icon-d2 | C | P | - |")
        self.assertIn("| icon-eu | - | - | - |", table)


if __name__ == "__main__":
    unittest.main()
