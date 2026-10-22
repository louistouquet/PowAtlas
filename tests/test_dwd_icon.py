import bz2
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import netCDF4

from fakes import FakeHttp
from gribfactory import make_message
from powatlas.adapters.dwd_icon import DwdIconAdapter, icon_url
from powatlas.catalogue import load_catalogue
from powatlas.grib import GridSpec
from powatlas.units import Unit

RUN = datetime(2026, 11, 1, tzinfo=timezone.utc)
SETTINGS = {"bbox": [5.0, 44.0, 6.0, 45.0], "margin_cells": 0}
SHORT = {"tot_prec": "tp", "t_2m": "2t"}


def small_source(steps=(0, 1, 2)):
    sources, _, _ = load_catalogue()
    real = sources["icon-d2"]
    return real.__class__(**{
        **real.__dict__,
        "steps": tuple(steps),
        "variables": {"tot_prec": {"shortName": "tp"}, "t_2m": {"shortName": "2t"}},
        "grid": GridSpec(ni=11, nj=6, lat_first=47.0, lon_first=4.0, di=0.5, dj=1.0),
    })


def message(var, step, date=20261101, **kw):
    accum = var == "tot_prec"
    rng = f"0-{step}" if accum and step else str(step)
    data = make_message(SHORT[var], date=date, step_range=rng, **kw)
    if var == "tot_prec" and step:
        # As in ICON-D2: the hourly message followed by quarter-hour messages.
        for minutes in (15, 30, 45):
            data += make_message("tp", date=date, step_units="m", step_range=f"0-{60 * step + minutes}", **kw)
    return bz2.compress(data)


def files_for(source, run=RUN, skip=(), date=20261101, **kw):
    return {
        icon_url(source, run, var, step): message(var, step, date=date, **kw)
        for var in source.variables for step in source.steps if (var, step) not in skip
    }


class IconUrlTest(unittest.TestCase):
    def test_icon_d2_url(self):
        sources, _, _ = load_catalogue()
        self.assertEqual(
            icon_url(sources["icon-d2"], RUN, "t_2m", 7),
            "https://opendata.dwd.de/weather/nwp/icon-d2/grib/00/t_2m/"
            "icon-d2_germany_regular-lat-lon_single-level_2026110100_007_2d_t_2m.grib2.bz2",
        )

    def test_icon_eu_url_uppercase(self):
        sources, _, _ = load_catalogue()
        self.assertEqual(
            icon_url(sources["icon-eu"], RUN, "tot_prec", 81),
            "https://opendata.dwd.de/weather/nwp/icon-eu/grib/00/tot_prec/"
            "icon-eu_europe_regular-lat-lon_single-level_2026110100_081_TOT_PREC.grib2.bz2",
        )


class IconAdapterTest(unittest.TestCase):
    def collect(self, source, files):
        out = Path(tempfile.mkdtemp())
        http = FakeHttp(files)
        m = DwdIconAdapter().collect(Unit(source.id, RUN), source, http, out, "daily", SETTINGS)
        return m, out, http

    def test_complete_unit(self):
        s = small_source()
        m, out, _ = self.collect(s, files_for(s))
        self.assertEqual(m.state, "complete")
        self.assertEqual(m.last_modified_max, "2026-11-01T01:04:00Z")
        with netCDF4.Dataset(out / m.files[0]["name"]) as ds:
            self.assertEqual(ds["tot_prec"].shape, (3, 2, 3))
            self.assertEqual(ds["tot_prec"].GRIB_shortName, "tp")
        self.assertEqual(len(m.fetched), 6)

    def test_404_for_some_steps_gives_partial(self):
        s = small_source()
        m, _, _ = self.collect(s, files_for(s, skip={("t_2m", 2)}))
        self.assertEqual((m.state, m.missing), ("partial", ["t_2m@2"]))

    def test_stale_previous_day_files_make_unit_partial(self):
        s = small_source()
        files = files_for(s)
        stale = files_for(s, date=20261031)
        files[icon_url(s, RUN, "tot_prec", 2)] = stale[icon_url(s, RUN, "tot_prec", 2)]
        m, _, _ = self.collect(s, files)
        self.assertEqual((m.state, m.missing), ("partial", ["tot_prec@2"]))
        self.assertTrue(any("2026-10-31" in n for n in m.notes))

    def test_grid_change_fails_unit(self):
        s = small_source()
        m, out, _ = self.collect(s, files_for(s, di=0.25))
        self.assertEqual(m.state, "missing")
        self.assertEqual(m.files, [])
        self.assertTrue(any("GridMismatch" in n for n in m.notes))

    def test_truncated_grib_gives_partial(self):
        s = small_source()
        files = files_for(s)
        files[icon_url(s, RUN, "t_2m", 1)] = bz2.compress(make_message("2t", step_range="1")[:-20])
        m, _, _ = self.collect(s, files)
        self.assertEqual((m.state, m.missing), ("partial", ["t_2m@1"]))

    def test_corrupt_bz2_gives_partial(self):
        s = small_source()
        files = files_for(s)
        files[icon_url(s, RUN, "t_2m", 1)] = b"<html>error</html>"
        files[icon_url(s, RUN, "t_2m", 2)] = bz2.compress(make_message("2t", step_range="2"))[:-30]
        m, _, _ = self.collect(s, files)
        self.assertEqual((m.state, m.missing), ("partial", ["t_2m@1", "t_2m@2"]))

    def test_inconsistent_grid_fails_unit(self):
        import eccodes
        s = small_source()
        files = files_for(s)
        h = eccodes.codes_new_from_message(make_message("2t", step_range="1"))
        eccodes.codes_set(h, "longitudeOfLastGridPointInDegrees", 9.5)
        files[icon_url(s, RUN, "t_2m", 1)] = bz2.compress(eccodes.codes_get_message(h))
        eccodes.codes_release(h)
        m, _, _ = self.collect(s, files)
        self.assertEqual(m.state, "missing")
        self.assertTrue(any("FormatChange" in n for n in m.notes))

    def test_stale_file_excluded_from_last_modified(self):
        s = small_source()
        files = files_for(s)
        stale = files_for(s, date=20261031)
        files[icon_url(s, RUN, "tot_prec", 2)] = stale[icon_url(s, RUN, "tot_prec", 2)]
        m, _, _ = self.collect(s, files)
        rejected = [f for f in m.fetched if f["rejected"]]
        self.assertEqual(len(rejected), 1)
        self.assertEqual(len(m.fetched), 6)

    def test_404_count_noted(self):
        s = small_source()
        m, _, _ = self.collect(s, {})
        self.assertEqual(m.state, "missing")
        self.assertTrue(any("HTTP 404 for all 6" in n for n in m.notes))

    def test_wrong_parameter_fails_unit(self):
        s = small_source()
        files = files_for(s)
        files[icon_url(s, RUN, "t_2m", 0)] = bz2.compress(make_message("tp", step_range="0"))
        m, _, _ = self.collect(s, files)
        self.assertEqual(m.state, "missing")
        self.assertTrue(any("shortName" in n for n in m.notes))


if __name__ == "__main__":
    unittest.main()
