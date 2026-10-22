import gzip
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import netCDF4
import numpy as np

from gribfactory import make_message
from powatlas.catalogue import Source
from powatlas.grib import iter_fields
from powatlas.units import Unit
from powatlas.writer import (
    Fetched,
    read_manifest,
    sha256_file,
    write_forecast_unit,
    write_observation_unit,
)

RUN = datetime(2026, 11, 1, tzinfo=timezone.utc)
T0 = datetime(2026, 11, 1, 2, 35, tzinfo=timezone.utc)


def src(kind="forecast"):
    return Source(
        id="icon-d2" if kind == "forecast" else "slf", family="x", kind=kind, task="t",
        fiche="docs/sources/icon-dwd.md", licence="CC BY 4.0", attribution="DWD", run_hours=(0,),
        steps=(0, 1, 2), variables={"tp": {}, "t2m": {}}, grid=None, window_days=0,
        available_after_hours=1.5, urls={},
    )


def field(step, value):
    (f,) = iter_fields(make_message(values=np.full((6, 11), value), step_range=str(step)))
    return f


class ForecastWriterTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.expected = [(v, s) for v in ("tp", "t2m") for s in (0, 1, 2)]

    def write(self, fields, fetched=None):
        return write_forecast_unit(
            self.tmp, Unit("icon-d2", RUN), src(), fields, self.expected,
            fetched or [Fetched("https://x/a", None, 10)], mode="daily", stream=None, collected_start=T0,
        )

    def test_forecast_round_trip(self):
        fields = {(v, s): field(s, 10 * i + s) for i, v in enumerate(("tp", "t2m")) for s in (0, 1, 2)}
        m = self.write(fields)
        self.assertEqual(m.state, "complete")
        self.assertEqual(m.missing, [])
        path = self.tmp / m.files[0]["name"]
        self.assertEqual(path.name, "icon-d2_20261101T00Z.nc")
        self.assertEqual(m.files[0]["sha256"], sha256_file(path))
        with netCDF4.Dataset(path) as ds:
            self.assertEqual(ds["tp"].dtype, np.float32)
            self.assertEqual(ds["step"][:].tolist(), [0, 1, 2])
            self.assertEqual(ds["tp"].dimensions, ("step", "lat", "lon"))
            np.testing.assert_array_equal(ds["t2m"][2], np.full((6, 11), 12.0))
            self.assertEqual(ds.reference_time, "2026-11-01T00:00:00Z")
            self.assertEqual(ds["tp"].GRIB_shortName, "tp")
            self.assertTrue(ds["tp"].filters()["zlib"] and ds["tp"].filters()["shuffle"])

    def test_missing_step_makes_partial(self):
        fields = {(v, s): field(s, 1) for v in ("tp", "t2m") for s in (0, 1, 2) if (v, s) != ("tp", 2)}
        m = self.write(fields)
        self.assertEqual(m.state, "partial")
        self.assertEqual(m.missing, ["tp@2"])
        with netCDF4.Dataset(self.tmp / m.files[0]["name"]) as ds:
            ds.set_auto_mask(False)
            self.assertTrue(np.all(np.isnan(ds["tp"][2])))

    def test_no_field_makes_missing_without_file(self):
        m = self.write({}, fetched=[])
        self.assertEqual(m.state, "missing")
        self.assertEqual(m.files, [])
        self.assertTrue((self.tmp / "icon-d2_20261101T00Z.json").is_file())

    def test_last_modified_range_recorded(self):
        lm = [datetime(2026, 11, 1, h, tzinfo=timezone.utc) for h in (1, 3, 2)]
        fields = {(v, s): field(s, 1) for v in ("tp", "t2m") for s in (0, 1, 2)}
        m = self.write(fields, [Fetched(f"https://x/{i}", t, 5) for i, t in enumerate(lm)])
        self.assertEqual(m.last_modified_min, "2026-11-01T01:00:00Z")
        self.assertEqual(m.last_modified_max, "2026-11-01T03:00:00Z")

    def test_different_grids_rejected(self):
        fields = {(v, s): field(s, 1) for v in ("tp", "t2m") for s in (0, 1, 2)}
        (other,) = iter_fields(make_message(ni=10, step_range="2"))
        fields[("tp", 2)] = other
        with self.assertRaises(ValueError):
            self.write(fields)

    def test_no_signed_link_in_manifest(self):
        fields = {(v, s): field(s, 1) for v in ("tp", "t2m") for s in (0, 1, 2)}
        for url in ("https://b/x?X-Amz-Signature=abc", "https://b/x?sig=abc&se=1"):
            with self.assertRaises(ValueError):
                self.write(fields, [Fetched(url, None, 1)])

    def test_manifest_round_trip(self):
        fields = {(v, s): field(s, 1) for v in ("tp", "t2m") for s in (0, 1, 2)}
        m = self.write(fields)
        again = read_manifest(self.tmp / "icon-d2_20261101T00Z.json")
        self.assertEqual(again, m)
        self.assertEqual(again.fiche, "docs/sources/icon-dwd.md")
        self.assertEqual(again.unit, "icon-d2__20261101T00Z")


class ObservationWriterTest(unittest.TestCase):
    def test_observation_payload_kept_verbatim(self):
        tmp = Path(tempfile.mkdtemp())
        payload = b'{"a": 1}\n' * 50
        m = write_observation_unit(
            tmp, Unit("slf", RUN), src("observation"),
            [("daily-snow.json", payload, Fetched("https://api/x", None, len(payload)))],
            expected=["daily-snow.json"], mode="daily", collected_start=T0,
        )
        self.assertEqual(m.state, "complete")
        name = m.files[0]["name"]
        self.assertEqual(name, "slf_20261101T0235Z_daily-snow.json.gz")
        self.assertEqual(gzip.decompress((tmp / name).read_bytes()), payload)

    def test_missing_payload_gives_partial(self):
        tmp = Path(tempfile.mkdtemp())
        m = write_observation_unit(
            tmp, Unit("slf", RUN), src("observation"),
            [("a.json", b"x", Fetched("https://api/a", None, 1))],
            expected=["a.json", "b.json"], mode="daily", collected_start=T0,
        )
        self.assertEqual((m.state, m.missing), ("partial", ["b.json"]))


if __name__ == "__main__":
    unittest.main()
