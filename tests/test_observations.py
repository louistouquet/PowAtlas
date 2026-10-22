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
SLF = "https://measurement-api.slf.ch/public/api/"
MF = "https://meteofrance.s3.sbg.io.cloud.ovh.net/"
QUOT = "data/synchro_ftp/BASE/QUOT/"
DEPS = ("04", "05", "06", "38", "73", "74")
IMIS_STATIONS = [
    {"code": "ARO1", "lon": 7.48, "lat": 46.03, "type": "SNOW_FLAT"},
    {"code": "FUL2", "lon": 7.9, "lat": 46.3, "type": "WIND"},
    {"code": "DAV2", "lon": 9.82, "lat": 46.70, "type": "SNOW_FLAT"},
]
PLOTS = [{"code": "4AO0", "lon": 7.48, "lat": 46.03}, {"code": "5WJ", "lon": 9.81, "lat": 46.83}]


def listing(dep, season="2026-2027"):
    return (f"<ListBucketResult><Contents><Key>{QUOT}Q_{dep}_latest-{season}_RR-T-Vent.csv.gz</Key></Contents>"
            f"<Contents><Key>{QUOT}Q_{dep}_latest-{season}_autres-parametres.csv.gz</Key></Contents>"
            "</ListBucketResult>").encode()


def listing_url(dep):
    return f"{MF}?list-type=2&prefix={QUOT}Q_{dep}_latest"


def slf_files():
    files = {SLF + "imis/stations": json.dumps(IMIS_STATIONS).encode(),
             SLF + "study-plot/stations": json.dumps(PLOTS).encode(),
             SLF + "imis/daily-snow?period_in_days=7": b"[1]"}
    for code in ("ARO1", "FUL2"):
        files[f"{SLF}imis/station/{code}/measurements?period_in_days=7"] = f'[{{"s": "{code}"}}]'.encode()
        files[f"{SLF}imis/station/{code}/measurements-precipitation?period_in_days=7"] = b"[2]"
    files[f"{SLF}study-plot/station/4AO0/measurements?period_in_days=7"] = b"[3]"
    return files


def collect(source_id, http, day=date(2026, 11, 1)):
    out = Path(tempfile.mkdtemp())
    unit = Unit(source_id, datetime(day.year, day.month, day.day, tzinfo=timezone.utc))
    return SnapshotAdapter().collect(unit, SOURCES[source_id], http, out, "daily", SETTINGS), out


class SlfTest(unittest.TestCase):
    def test_slf_per_station_routes_limited_to_domain(self):
        items, failures = snapshot_items(SOURCES["slf"], date(2026, 11, 1), FakeHttp(slf_files()), SETTINGS)
        urls = {i.url for i in items}
        self.assertEqual(failures, [])
        self.assertIn(f"{SLF}imis/station/ARO1/measurements?period_in_days=7", urls)
        self.assertIn(f"{SLF}imis/station/FUL2/measurements-precipitation?period_in_days=7", urls)
        self.assertIn(f"{SLF}study-plot/station/4AO0/measurements?period_in_days=7", urls)
        self.assertFalse(any("DAV2" in u or "5WJ" in u for u in urls))
        self.assertEqual(len(items), 3 + 2 * 2 + 1)

    def test_imis_daily_snow_marked_modelled(self):
        self.assertIn("modelled", SOURCES["slf"].variables["imis-daily-snow.json"]["nature"])

    def test_complete_snapshot_kept_verbatim(self):
        files = slf_files()
        m, out = collect("slf", FakeHttp(files))
        self.assertEqual(m.state, "complete")
        f = next(f for f in m.files if "imis-measurements_ARO1" in f["name"])
        self.assertEqual(gzip.decompress((out / f["name"]).read_bytes()),
                         files[f"{SLF}imis/station/ARO1/measurements?period_in_days=7"])

    def test_precipitation_station_not_found_is_optional(self):
        files = slf_files()
        url = f"{SLF}imis/station/ARO1/measurements-precipitation?period_in_days=7"
        del files[url]
        m, _ = collect("slf", FakeHttp(files, errors={url: 400}))
        self.assertEqual(m.state, "complete")

    def test_station_without_data_is_noted_not_lost(self):
        # Per-station routes answer 404 when a station has no data in the period
        # (study plots out of season, stations without the sensor).
        files = slf_files()
        del files[f"{SLF}study-plot/station/4AO0/measurements?period_in_days=7"]
        m, _ = collect("slf", FakeHttp(files))
        self.assertEqual(m.state, "complete")
        self.assertIn("study-plot-measurements: no data for 1 of 1 stations (4AO0)", m.notes)

    def test_failed_route_gives_partial(self):
        files = slf_files()
        url = f"{SLF}imis/station/ARO1/measurements?period_in_days=7"
        m, _ = collect("slf", FakeHttp(files, errors={url: 500}))
        self.assertEqual((m.state, m.missing), ("partial", ["imis-measurements_ARO1.json"]))

    def test_station_list_failure_gives_partial(self):
        files = slf_files()
        del files[SLF + "imis/stations"]
        m, _ = collect("slf", FakeHttp(files))
        self.assertEqual(m.state, "partial")
        self.assertIn("imis-stations.json", m.missing)


class ArpaTest(unittest.TestCase):
    def arpa_files(self):
        return {"https://utility.arpa.piemonte.it/api_realtime/pie_neve": b"[{}]",
                "https://utility.arpa.piemonte.it/api_realtime/pie_anag": b"[{}]"}

    def test_problem_json_is_failure(self):
        files = self.arpa_files()
        files["https://utility.arpa.piemonte.it/api_realtime/pie_neve"] = json.dumps(
            {"type": "about:blank", "title": "Error", "status": 500}).encode()
        m, _ = collect("arpa-piemonte", FakeHttp(files))
        self.assertEqual((m.state, m.missing), ("partial", ["pie-neve.json"]))

    def test_non_json_answer_is_failure(self):
        files = self.arpa_files()
        files["https://utility.arpa.piemonte.it/api_realtime/pie_anag"] = b"<html>maintenance</html>"
        m, _ = collect("arpa-piemonte", FakeHttp(files))
        self.assertEqual((m.state, m.missing), ("partial", ["pie-anag.json"]))

    def test_response_headers_recorded(self):
        m, _ = collect("arpa-piemonte", FakeHttp(self.arpa_files(), headers={"ETag": '"abc"', "Age": "12"}))
        self.assertEqual(m.fetched[0]["headers"], {"ETag": '"abc"', "Age": "12"})


class MeteoFranceTest(unittest.TestCase):
    def test_new_year_collects_both_nivo_files(self):
        old = MF + "data/OBS/NIVOSE/nivo_2026.csv.gz"
        new = MF + "data/OBS/NIVOSE/nivo_2027.csv.gz"
        items, _ = snapshot_items(SOURCES["meteofrance-nivo"], date(2027, 1, 3), FakeHttp({}), SETTINGS)
        self.assertEqual(sorted(i.url for i in items), [old, new])
        m, _ = collect("meteofrance-nivo", FakeHttp({old: gzip.compress(b"a;b\n")}), day=date(2027, 1, 3))
        self.assertEqual(m.state, "complete")
        later, _ = snapshot_items(SOURCES["meteofrance-nivo"], date(2027, 1, 8), FakeHttp({}), SETTINGS)
        self.assertEqual([i.url for i in later], [new])

    def test_gzip_payload_not_recompressed(self):
        url = MF + "data/OBS/NIVOSE/nivo_2026.csv.gz"
        raw = gzip.compress(b"numer_sta;date\n")
        m, out = collect("meteofrance-nivo", FakeHttp({url: raw}))
        self.assertEqual(m.files[0]["name"].count(".gz"), 1)
        self.assertEqual((out / m.files[0]["name"]).read_bytes(), raw)

    def test_file_not_refreshed_today_noted(self):
        url = MF + "data/OBS/NIVOSE/nivo_2026.csv.gz"
        old = datetime(2026, 10, 31, 6, 30, tzinfo=timezone.utc)
        m, _ = collect("meteofrance-nivo", FakeHttp({url: gzip.compress(b"x")}, last_modified=old))
        self.assertTrue(any("not refreshed" in n for n in m.notes))

    def test_quot_season_name_discovered_for_each_department(self):
        http = FakeHttp({listing_url(d): listing(d) for d in DEPS})
        items, failures = snapshot_items(SOURCES["meteofrance-quot"], date(2027, 1, 2), http, SETTINGS)
        self.assertEqual((len(items), failures), (6, []))
        self.assertIn(MF + QUOT + "Q_38_latest-2026-2027_autres-parametres.csv.gz", [i.url for i in items])

    def test_quot_listing_failure_gives_partial(self):
        files = {listing_url(d): listing(d) for d in DEPS if d != "05"}
        files.update({MF + QUOT + f"Q_{d}_latest-2026-2027_autres-parametres.csv.gz": gzip.compress(b"x")
                      for d in DEPS})
        m, _ = collect("meteofrance-quot", FakeHttp(files), day=date(2027, 1, 2))
        self.assertEqual(m.state, "partial")
        self.assertEqual(m.missing, ["Q_05 listing"])


if __name__ == "__main__":
    unittest.main()
