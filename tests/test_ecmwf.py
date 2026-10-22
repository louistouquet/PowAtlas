import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from fakes import FakeHttp
from gribfactory import make_message
from powatlas.adapters.ecmwf import EcmwfAdapter, ecmwf_path
from powatlas.catalogue import Source, expected_pairs, load_catalogue
from powatlas.grib import GridSpec
from powatlas.indexes import IndexEntry, parse_ecmwf_index
from powatlas.units import Unit

RUN = datetime(2026, 11, 1, tzinfo=timezone.utc)
SETTINGS = {"bbox": [5.0, 44.0, 6.0, 45.0], "margin_cells": 0}
PORTAL = "https://data.ecmwf.int/forecasts/"


def msg(short, step, **kw):
    rng = f"0-{step}" if short == "tp" else str(step)
    return make_message(short, step_range=rng, **kw)


def build(step_fields, extra_step_entries=()):
    """Index (JSON lines) and GRIB file for one step: [(param, levtype, levelist, bytes)]."""
    lines, data = [], b""
    for param, levtype, levelist, m, step in step_fields:
        row = {"param": param, "levtype": levtype, "step": str(step), "_offset": len(data), "_length": len(m)}
        if levelist is not None:
            row["levelist"] = levelist
        lines.append(json.dumps(row))
        data += m
    return "\n".join(lines).encode(), data


def source():
    real = load_catalogue()[0]["ifs-0p25"]
    return Source(**{**real.__dict__, "steps": (0, 3),
                     "variables": {"tp": {"param": "tp", "levtype": "sfc"}, "2t": {"param": "2t", "levtype": "sfc"},
                                   "t_850": {"param": "t", "levtype": "pl", "levelist": "850"}},
                     "grid": GridSpec(ni=11, nj=6, lat_first=47.0, lon_first=4.0, di=0.5, dj=1.0)})


def files(skip_step=None, date=20261101):
    out = {}
    for step in (0, 3):
        if step == skip_step:
            continue
        fields = [("tp", "sfc", None, msg("tp", step, date=date), step),
                  ("10u", "sfc", None, msg("10u", step, type_of_level="heightAboveGround", level=10), step),
                  ("2t", "sfc", None, msg("2t", step, type_of_level="heightAboveGround", level=2, date=date), step),
                  ("t", "pl", "850", msg("t", step, type_of_level="isobaricInhPa", level=850, date=date), step),
                  ("t", "pl", "500", msg("t", step, type_of_level="isobaricInhPa", level=500), step)]
        if step == 0:  # as in the real 0 h index: a 3-hourly minimum labelled step 3
            fields.append(("mn2t3", "sfc", None, msg("2t", 3), 3))
        index, data = build(fields)
        base = PORTAL + ecmwf_path("ifs", RUN, step)
        out[base + ".index"], out[base + ".grib2"] = index, data
    return out


def collect(served):
    http = FakeHttp(served)
    m = EcmwfAdapter().collect(Unit("ifs-0p25", RUN), source(), http, Path(tempfile.mkdtemp()), "daily", SETTINGS)
    return m, http


class EcmwfTest(unittest.TestCase):
    def test_parse_index_lines(self):
        text = b'{"param": "sf", "levtype": "sfc", "step": "24", "_offset": 10, "_length": 5}\n' \
               b'{"param": "t", "levtype": "pl", "levelist": "850", "step": "24", "_offset": 15, "_length": 7}\n'
        self.assertEqual(parse_ecmwf_index(text), [IndexEntry("sf", "sfc", None, "24", 10, 5),
                                                    IndexEntry("t", "pl", "850", "24", 15, 7)])

    def test_path_before_and_after_layout_switch(self):
        self.assertEqual(ecmwf_path("ifs", datetime(2024, 2, 28, tzinfo=timezone.utc), 24),
                         "20240228/00z/0p25/oper/20240228000000-24h-oper-fc")
        self.assertEqual(ecmwf_path("ifs", datetime(2024, 2, 29, tzinfo=timezone.utc), 24),
                         "20240229/00z/ifs/0p25/oper/20240229000000-24h-oper-fc")
        self.assertEqual(ecmwf_path("aifs-single", RUN, 6), "20261101/00z/aifs-single/0p25/oper/20261101000000-6h-oper-fc")

    def test_complete_unit_fetches_only_wanted_fields(self):
        served = files()
        m, http = collect(served)
        self.assertEqual((m.state, m.missing), ("complete", []))
        grib_bytes = sum(r[1] - r[0] + 1 for u, r in http.requests if u.endswith(".grib2"))
        self.assertEqual(grib_bytes, sum(len(msg(s, st, **kw)) for st in (0, 3) for s, kw in
                                         (("tp", {}), ("2t", {"type_of_level": "heightAboveGround", "level": 2}),
                                          ("t", {"type_of_level": "isobaricInhPa", "level": 850}))))

    def test_entry_labelled_with_another_step_ignored(self):
        m, _ = collect(files())
        self.assertFalse(any("two" in n for n in m.notes))

    def test_missing_index_gives_partial(self):
        m, _ = collect(files(skip_step=3))
        self.assertEqual((m.state, m.missing), ("partial", ["tp@3", "2t@3", "t_850@3"]))

    def test_stale_run_rejected(self):
        m, _ = collect(files(date=20261031))
        self.assertEqual(m.state, "missing")


class CatalogueEcmwfTest(unittest.TestCase):
    def test_ifs_and_aifs_declared(self):
        sources, tasks, _ = load_catalogue()
        ifs, aifs = sources["ifs-0p25"], sources["aifs-single"]
        self.assertEqual((len(ifs.steps), len(aifs.steps)), (85, 61))
        pairs = expected_pairs(ifs)
        self.assertNotIn(("mn2t3", 0), pairs)
        self.assertIn(("mn2t3", 144), pairs)
        self.assertNotIn(("mn2t3", 150), pairs)
        self.assertIn(("mn2t6", 150), pairs)
        self.assertEqual(set(aifs.variables), {"sf", "tp", "2t", "tcc", "10u", "10v"})
        self.assertEqual(tasks["ecmwf"].crons, ("50 8 * * *", "50 14 * * *"))
        self.assertEqual(ifs.window_days, 2)


if __name__ == "__main__":
    unittest.main()
