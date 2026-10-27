import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import powatlas.adapters.all  # noqa: F401  (registers the adapters)
from fakes import FakeHttp
from powatlas import collect
from powatlas.catalogue import load_catalogue
from powatlas.pc import collect_pc, dates_in_payload, store_copies
from powatlas.writer import sha256_file

SOURCES, TASKS, SETTINGS = load_catalogue()
NOW = datetime(2026, 10, 27, 11, 0, tzinfo=timezone.utc)
ARPA = "https://utility.arpa.piemonte.it/api_realtime/"
ARCHIVE = Path("observations") / "arpa-piemonte" / "2026" / "10"


def arpa_http():
    return FakeHttp({ARPA + "pie_neve": b'[{"data": "2026-10-21"}]', ARPA + "pie_anag": b'[{"id": 1}]'})


def copy_dir(root, uid="arpa-piemonte__20261027", state="complete", files=None, corrupt=False):
    """A unit folder as written by ``powatlas collect --out <root>``: data files plus the manifest."""
    source, ref = uid.split("__")
    folder = Path(root) / uid
    folder.mkdir(parents=True)
    files = files if files is not None else {f"{source}_{ref}T0745Z_pie-neve.json.gz": b"neve",
                                             f"{source}_{ref}T0745Z_pie-anag.json.gz": b"anag"}
    entries = []
    for name, content in files.items():
        (folder / name).write_bytes(content)
        entries.append({"name": name, "sha256": sha256_file(folder / name), "size": len(content)})
    if corrupt:
        (folder / next(iter(files))).write_bytes(b"tampered")
    manifest = {"unit": uid, "source": source, "state": state, "files": entries, "missing": []}
    (folder / f"{source}_{ref}.json").write_text(json.dumps(manifest), encoding="utf-8")
    return folder


class ArpaOnThePcTest(unittest.TestCase):
    def test_arpa_is_collected_on_the_pc_not_on_actions(self):
        self.assertEqual(SOURCES["arpa-piemonte"].task, "pc")
        units = collect.plan("observations", NOW, [], SOURCES, TASKS)
        self.assertFalse([u for u in units if u.startswith("arpa-piemonte")], units)
        self.assertIn("slf__20261027", units)


class StoreCopiesTest(unittest.TestCase):
    def setUp(self):
        self.data = Path(tempfile.mkdtemp())
        self.copies = self.data / "pc-collect"

    def test_copy_moved_into_archive_and_folder_removed(self):
        copy_dir(self.copies)
        r = store_copies(self.data, self.copies)
        self.assertEqual((r.new, r.replaced, r.kept, r.rejected), (1, 0, 0, []))
        target = self.data / ARCHIVE
        self.assertEqual(sorted(p.name for p in target.iterdir()),
                         ["arpa-piemonte_20261027.json", "arpa-piemonte_20261027T0745Z_pie-anag.json.gz",
                          "arpa-piemonte_20261027T0745Z_pie-neve.json.gz"])
        self.assertFalse((self.copies / "arpa-piemonte__20261027").exists())

    def test_altered_copy_rejected_and_left_in_place(self):
        copy_dir(self.copies, corrupt=True)
        r = store_copies(self.data, self.copies)
        self.assertEqual((r.new, r.rejected), (0, ["arpa-piemonte__20261027"]))
        self.assertFalse((self.data / ARCHIVE).exists())
        self.assertTrue((self.copies / "arpa-piemonte__20261027" / "arpa-piemonte_20261027.json").exists())

    def test_worse_copy_does_not_replace_complete_unit(self):
        copy_dir(self.data / "first")
        store_copies(self.data, self.data / "first")
        copy_dir(self.copies, state="partial", files={"arpa-piemonte_20261027T1200Z_pie-anag.json.gz": b"a"})
        r = store_copies(self.data, self.copies)
        self.assertEqual(r.kept, 1)
        manifest = json.loads((self.data / ARCHIVE / "arpa-piemonte_20261027.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["state"], "complete")
        self.assertTrue((self.data / ARCHIVE / "arpa-piemonte_20261027T0745Z_pie-neve.json.gz").exists())

    def test_equally_good_copy_does_not_replace_archived_unit(self):
        # A manual copy filed after collect-pc may be older than the archived unit of the same day.
        copy_dir(self.data / "first")
        store_copies(self.data, self.data / "first")
        copy_dir(self.copies, files={"arpa-piemonte_20261027T0600Z_pie-neve.json.gz": b"older",
                                     "arpa-piemonte_20261027T0600Z_pie-anag.json.gz": b"older"})
        r = store_copies(self.data, self.copies)
        self.assertEqual((r.new, r.replaced, r.kept), (0, 0, 1))
        self.assertTrue((self.data / ARCHIVE / "arpa-piemonte_20261027T0745Z_pie-neve.json.gz").exists())
        self.assertFalse((self.data / ARCHIVE / "arpa-piemonte_20261027T0600Z_pie-neve.json.gz").exists())

    def test_absent_copies_folder_is_nothing_to_do(self):
        r = store_copies(self.data, self.copies)
        self.assertEqual((r.new, r.replaced, r.kept, r.rejected), (0, 0, 0, []))


class CollectPcTest(unittest.TestCase):
    def setUp(self):
        self.data = Path(tempfile.mkdtemp())

    def test_today_unit_of_each_pc_observation_source_written_into_archive(self):
        results = collect_pc(self.data, arpa_http(), SOURCES, SETTINGS, NOW)
        self.assertEqual(results, [("arpa-piemonte__20261027", "complete", "new")])
        manifest = json.loads((self.data / ARCHIVE / "arpa-piemonte_20261027.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["state"], "complete")
        self.assertFalse(any((self.data / ".tmp").iterdir()))

    def test_collected_before_the_usual_hour(self):
        # The copy covers 7 days: a run early in the morning is still today's unit.
        early = NOW.replace(hour=5)
        results = collect_pc(self.data, arpa_http(), SOURCES, SETTINGS, early)
        self.assertEqual(results, [("arpa-piemonte__20261027", "complete", "new")])

    def test_unit_already_complete_in_archive_not_collected_again(self):
        collect_pc(self.data, arpa_http(), SOURCES, SETTINGS, NOW)
        http = arpa_http()
        results = collect_pc(self.data, http, SOURCES, SETTINGS, NOW.replace(hour=15))
        self.assertEqual(results, [("arpa-piemonte__20261027", "complete", "already complete")])
        self.assertEqual(http.requests, [])

    def test_unreachable_producer_leaves_complete_unit_untouched(self):
        collect_pc(self.data, arpa_http(), SOURCES, SETTINGS, NOW.replace(day=26))
        results = collect_pc(self.data, FakeHttp({}), SOURCES, SETTINGS, NOW)
        self.assertEqual(results, [("arpa-piemonte__20261027", "missing", "new")])
        days = sorted(p.name for p in (self.data / ARCHIVE).glob("*.json"))
        self.assertEqual(days, ["arpa-piemonte_20261026.json", "arpa-piemonte_20261027.json"])



    def test_failing_source_reported_and_others_still_collected(self):
        from powatlas import adapters

        class Broken:
            def collect(self, *a):
                raise OSError("file locked")

        import dataclasses
        sources = dict(SOURCES, broken=dataclasses.replace(SOURCES["arpa-piemonte"], id="broken", family="broken"))
        adapters.ADAPTERS["broken"] = Broken()
        try:
            results = collect_pc(self.data, arpa_http(), sources, SETTINGS, NOW)
        finally:
            del adapters.ADAPTERS["broken"]
        self.assertEqual(results, [("arpa-piemonte__20261027", "complete", "new"),
                                   ("broken__20261027", "missing", "error: file locked")])

class DatesTest(unittest.TestCase):
    def test_days_counted_in_any_string_value(self):
        payload = json.dumps([
            {"station": "A", "date": "2026-10-21T08:00:00+02:00", "validated_snow_height": 0},
            {"station": "B", "date": "2026-10-21", "nested": {"when": "2026-10-27 08:00"}},
            {"station": "C", "note": "not 2026-10-22", "code": 20261023},
        ]).encode()
        self.assertEqual(dates_in_payload(payload), {"2026-10-21": 2, "2026-10-27": 1})

    def test_gzip_payload_read(self):
        import gzip

        self.assertEqual(dates_in_payload(gzip.compress(b'{"results": [{"data": "2026-10-24"}]}')), {"2026-10-24": 1})

if __name__ == "__main__":
    unittest.main()
