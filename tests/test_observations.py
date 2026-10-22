import gzip
import json
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

from fakes import FakeHttp
from powatlas.adapters.observations import SnapshotAdapter, snapshot_items
from powatlas.catalogue import load_catalogue
from powatlas.units import Unit

SOURCES, TASKS, SETTINGS = load_catalogue()
SLF_API = "https://measurement-api.slf.ch/public/api/"
MF = "https://meteofrance.s3.sbg.io.cloud.ovh.net/"
LISTING = (
    "<ListBucketResult><Contents><Key>data/synchro_ftp/BASE/QUOT/Q_73_latest-2026-2027_RR-T-Vent.csv.gz</Key>"
    "</Contents><Contents><Key>data/synchro_ftp/BASE/QUOT/Q_73_latest-2026-2027_autres-parametres.csv.gz</Key>"
    "</Contents></ListBucketResult>"
).encode()


def collect(source_id, files, day=date(2026, 11, 1)):
    out = Path(tempfile.mkdtemp())
    unit = Unit(source_id, datetime(day.year, day.month, day.day, tzinfo=timezone.utc))
    m = SnapshotAdapter().collect(unit, SOURCES[source_id], FakeHttp(files), out, "daily", SETTINGS)
    return m, out


class ObservationsTest(unittest.TestCase):
    def test_slf_routes(self):
        urls = sorted(i.url for i in snapshot_items(SOURCES["slf"], date(2026, 11, 1), FakeHttp({})))
        self.assertEqual(urls, sorted(SLF_API + r for r in (
            "imis/stations", "imis/measurements", "imis/measurements-precipitation",
            "imis/daily-snow?period_in_days=7", "study-plot/stations", "study-plot/measurements")))

    def test_imis_daily_snow_marked_modelled(self):
        self.assertIn("modelled", SOURCES["slf"].variables["imis-daily-snow.json"]["nature"])

    def test_complete_snapshot_kept_verbatim(self):
        files = {i.url: json.dumps([{"i": n}]).encode()
                 for n, i in enumerate(snapshot_items(SOURCES["slf"], date(2026, 11, 1), FakeHttp({})))}
        m, out = collect("slf", files)
        self.assertEqual(m.state, "complete")
        self.assertEqual(len(m.files), 6)

    def test_failed_route_gives_partial(self):
        items = snapshot_items(SOURCES["slf"], date(2026, 11, 1), FakeHttp({}))
        files = {i.url: b"[1]" for i in items if "study-plot/measurements" not in i.url}
        m, _ = collect("slf", files)
        self.assertEqual((m.state, m.missing), ("partial", ["study-plot-measurements.json"]))

    def test_problem_json_is_failure(self):
        items = snapshot_items(SOURCES["arpa-piemonte"], date(2026, 11, 1), FakeHttp({}))
        files = {i.url: b"[{}]" for i in items}
        files[items[0].url] = json.dumps({"type": "about:blank", "title": "Error", "status": 500}).encode()
        m, _ = collect("arpa-piemonte", files)
        self.assertEqual(m.state, "partial")
        self.assertTrue(m.notes)

    def test_new_year_collects_both_nivo_files(self):
        old = MF + "data/OBS/NIVOSE/nivo_2026.csv.gz"
        new = MF + "data/OBS/NIVOSE/nivo_2027.csv.gz"
        items = snapshot_items(SOURCES["meteofrance-nivo"], date(2027, 1, 3), FakeHttp({}))
        self.assertEqual(sorted(i.url for i in items), [old, new])
        m, _ = collect("meteofrance-nivo", {old: gzip.compress(b"a;b\n")}, day=date(2027, 1, 3))
        self.assertEqual(m.state, "complete")
        later = snapshot_items(SOURCES["meteofrance-nivo"], date(2027, 1, 8), FakeHttp({}))
        self.assertEqual([i.url for i in later], [new])

    def test_gzip_payload_not_recompressed(self):
        url = MF + "data/OBS/NIVOSE/nivo_2026.csv.gz"
        raw = gzip.compress(b"numer_sta;date\n")
        m, out = collect("meteofrance-nivo", {url: raw})
        self.assertEqual(m.files[0]["name"].count(".gz"), 1)
        self.assertEqual((out / m.files[0]["name"]).read_bytes(), raw)

    def test_quot_season_name_discovered_from_listing(self):
        http = FakeHttp({MF + "?list-type=2&prefix=data/synchro_ftp/BASE/QUOT/Q_73_latest": LISTING})
        urls = [i.url for i in snapshot_items(SOURCES["meteofrance-quot"], date(2027, 1, 2), http)]
        self.assertEqual(len(urls), 6)
        self.assertIn(MF + "data/synchro_ftp/BASE/QUOT/Q_38_latest-2026-2027_autres-parametres.csv.gz", urls)

    def test_quot_without_season_in_listing_fails_loudly(self):
        http = FakeHttp({MF + "?list-type=2&prefix=data/synchro_ftp/BASE/QUOT/Q_73_latest": b"<ListBucketResult/>"})
        with self.assertRaises(ValueError):
            snapshot_items(SOURCES["meteofrance-quot"], date(2027, 1, 2), http)


if __name__ == "__main__":
    unittest.main()
