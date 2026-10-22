import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from fakes import FakeHttp
from gribfactory import make_message
from powatlas.adapters.gfs import GfsAdapter, gfs_url
from powatlas.catalogue import Source, load_catalogue
from powatlas.grib import GridSpec
from powatlas.indexes import parse_gfs_idx
from powatlas.units import Unit

RUN = datetime(2026, 1, 1, tzinfo=timezone.utc)
SETTINGS = {"bbox": [5.0, 44.0, 6.0, 45.0], "margin_cells": 0, "collect_budget_minutes": 75}


def source():
    real = load_catalogue()[0]["gfs-0p25"]
    return Source(**{**real.__dict__, "steps": (0, 3),
                     "variables": {"2t": {"var": "TMP", "level": "2 m above ground", "time": "instant", "shortName": "2t"},
                                   "tp": {"var": "APCP", "level": "surface", "time": "acc-from-run-start",
                                          "shortName": "tp", "steps": [[3, 3, 3]]}},
                     "grid": GridSpec(ni=11, nj=6, lat_first=47.0, lon_first=4.0, di=0.5, dj=1.0)})


def step_file(step, date=20260101):
    t2m = make_message("2t", step_range=str(step), type_of_level="heightAboveGround", level=2, date=date)
    msgs = [("TMP", "2 m above ground", "anl" if step == 0 else f"{step} hour fcst", t2m)]
    if step:
        msgs += [("APCP", "surface", f"0-{step} hour acc fcst", make_message("tp", step_range=f"0-{step}", date=date)),
                 ("APCP", "surface", f"0-{step} hour acc fcst", make_message("tp", step_range=f"0-{step}", date=date)),
                 ("PRATE", "surface", f"{step} hour fcst", make_message("2t", step_range=str(step)))]
    # Real files end with many other records: the selected ones are never last.
    msgs.append(("HGT", "surface", "anl" if step == 0 else f"{step} hour fcst", make_message("2t", step_range=str(step))))
    data, lines, off = b"", [], 0
    for n, (var, level, desc, m) in enumerate(msgs, start=1):
        lines.append(f"{n}:{off}:d=2026010100:{var}:{level}:{desc}:")
        data += m
        off += len(m)
    return "\n".join(lines).encode() + b"\n", data


def served(date=20260101):
    out = {}
    for step in (0, 3):
        idx, data = step_file(step, date)
        out[gfs_url(RUN, step) + ".idx"], out[gfs_url(RUN, step)] = idx, data
    return out


def collect(files, mode="backfill"):
    http = FakeHttp(files)
    return GfsAdapter().collect(Unit("gfs-0p25", RUN), source(), http, Path(tempfile.mkdtemp()), mode, SETTINGS), http


class GfsTest(unittest.TestCase):
    def test_parse_gfs_idx_lengths(self):
        text = b"1:0:d=2026010100:TMP:2 m above ground:anl:\n2:100:d=2026010100:APCP:surface:0-3 hour acc fcst:\n" \
               b"3:250:d=2026010100:PRATE:surface:3 hour fcst:\n"
        entries = parse_gfs_idx(text)
        self.assertEqual([(e.var, e.level, e.desc, e.offset, e.length) for e in entries],
                         [("TMP", "2 m above ground", "anl", 0, 100), ("APCP", "surface", "0-3 hour acc fcst", 100, 150),
                          ("PRATE", "surface", "3 hour fcst", 250, None)])

    def test_url(self):
        self.assertEqual(gfs_url(RUN, 24),
                         "https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs.20260101/00/atmos/gfs.t00z.pgrb2.0p25.f024")

    def test_complete_unit_first_duplicate_kept(self):
        m, _ = collect(served())
        self.assertEqual((m.state, m.missing), ("complete", []))
        self.assertEqual(m.stream, "atmos/pgrb2.0p25")
        self.assertIn("NOAA", m.attribution)

    def test_stale_run_rejected(self):
        m, _ = collect(served(date=20251231))
        self.assertEqual(m.state, "missing")

    def test_gfs_attribution_includes_noaa_clause(self):
        a = load_catalogue()[0]["gfs-0p25"].attribution
        self.assertIn("not the original", a)


if __name__ == "__main__":
    unittest.main()
