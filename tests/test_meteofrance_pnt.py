import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import eccodes

from fakes import FakeHttp
from gribfactory import make_message
from powatlas.adapters.meteofrance_pnt import MeteoFrancePntAdapter, group_steps
from powatlas.catalogue import Source, load_catalogue
from powatlas.grib import GridSpec
from powatlas.units import Unit

RUN = datetime(2026, 11, 1, tzinfo=timezone.utc)
ISO = "2026-11-01T00:00:00Z"
BASE = "https://meteofrance-pnt.s3.rbx.io.cloud.ovh.net/"
PREFIX = f"pnt/{ISO}/arome/0025/SP1/"
SETTINGS = {"bbox": [5.0, 44.0, 6.0, 45.0], "margin_cells": 0}


def identity(msg):
    h = eccodes.codes_new_from_message(msg)
    try:
        g = lambda k: eccodes.codes_get_long(h, k)
        scale = g("scaleFactorOfFirstFixedSurface") if eccodes.codes_is_defined(h, "scaleFactorOfFirstFixedSurface") else None
        value = None if eccodes.codes_is_missing(h, "scaledValueOfFirstFixedSurface") else float(g("scaledValueOfFirstFixedSurface"))
        return [g("discipline"), g("parameterCategory"), g("parameterNumber"), g("typeOfFirstFixedSurface"), value]
    finally:
        eccodes.codes_release(h)


def t2m(step, date=20261101):
    return make_message("2t", step_range=str(step), type_of_level="heightAboveGround", level=2, date=date)


def tp(step, date=20261101):
    return make_message("tp", step_range=f"0-{step}", date=date)


def u10(step):
    return make_message("10u", step_range=str(step), type_of_level="heightAboveGround", level=10)


def source():
    real = load_catalogue()[0]["arome-0025"]
    return Source(**{
        **real.__dict__,
        "steps": (0, 1, 2, 3),
        "variables": {"2t": {"shortName": "2t", "package": "SP1", "grib": identity(t2m(0))},
                      "tp": {"shortName": "tp", "package": "SP1", "grib": identity(tp(1)), "steps": [[1, 3, 1]]}},
        "grid": GridSpec(ni=11, nj=6, lat_first=47.0, lon_first=4.0, di=0.5, dj=1.0),
    })


def listing(files):
    body = "".join(f"<Contents><Key>{PREFIX}{name}</Key><LastModified>2026-11-01T02:54:00.000Z</LastModified>"
                   f"<Size>{len(data)}</Size></Contents>" for name, data in files.items())
    return f"<ListBucketResult>{body}</ListBucketResult>".encode()


def name(group):
    return f"arome__0025__SP1__{group}__{ISO}.grib2"


def standard_files():
    return {
        name("00H01H"): t2m(0) + u10(0) + t2m(1) + tp(1) + u10(1),
        name("02H03H"): t2m(2) + tp(2) + u10(2) + t2m(3) + tp(3),
    }


def http_for(files):
    served = {BASE + PREFIX + n: d for n, d in files.items()}
    served[f"{BASE}?list-type=2&prefix={PREFIX}"] = listing(files)
    return FakeHttp(served)


def collect(files, src=None):
    http = http_for(files)
    m = MeteoFrancePntAdapter().collect(Unit("arome-0025", RUN), src or source(), http, Path(tempfile.mkdtemp()),
                                        "catchup", SETTINGS)
    return m, http


class PntTest(unittest.TestCase):
    def test_group_steps(self):
        self.assertEqual(group_steps(name("49H51H")), (49, 51))
        self.assertEqual(group_steps("arpege__01__SP1__097H102H__2026-11-01T00:00:00Z.grib2"), (97, 102))

    def test_complete_unit(self):
        m, _ = collect(standard_files())
        self.assertEqual((m.state, m.missing, m.mode), ("complete", [], "catchup"))
        self.assertEqual(m.last_modified_max, "2026-11-01T01:04:00Z")

    def test_selects_only_catalogue_messages(self):
        files = standard_files()
        m, http = collect(files)
        from collections import Counter
        reads = Counter((u, r) for u, r in http.requests if r is not None)
        for n, data in files.items():  # remove one header read per message
            offset = 0
            while offset < len(data):
                reads[(BASE + PREFIX + n, (offset, min(offset + 1024, len(data)) - 1))] -= 1
                offset += int.from_bytes(data[offset + 8 : offset + 16], "big")
        self.assertTrue(all(c >= 0 for c in reads.values()))
        fetched = sum((r[1] - r[0] + 1) * c for (_, r), c in reads.items())
        wanted = sum(len(x) for x in (t2m(0), t2m(1), tp(1), t2m(2), tp(2), t2m(3), tp(3)))
        self.assertEqual(fetched, wanted)

    def test_missing_group_file_gives_partial(self):
        files = standard_files()
        del files[name("02H03H")]
        m, _ = collect(files)
        self.assertEqual((m.state, m.missing), ("partial", ["2t@2", "2t@3", "tp@2", "tp@3"]))

    def test_stale_run_rejected(self):
        files = standard_files()
        files[name("02H03H")] = t2m(2, date=20261031) + tp(2) + t2m(3) + tp(3)
        m, _ = collect(files)
        self.assertEqual((m.state, m.missing), ("partial", ["2t@2"]))

    def test_duplicate_message_fails_unit(self):
        files = standard_files()
        files[name("02H03H")] = t2m(2) + t2m(2) + tp(2) + t2m(3) + tp(3)
        m, _ = collect(files)
        self.assertEqual(m.state, "missing")
        self.assertTrue(any("FormatChange" in n for n in m.notes))

    def test_listing_failure_gives_missing_with_note(self):
        http = FakeHttp({})
        m = MeteoFrancePntAdapter().collect(Unit("arome-0025", RUN), source(), http, Path(tempfile.mkdtemp()),
                                            "daily", SETTINGS)
        self.assertEqual(m.state, "missing")
        self.assertTrue(any("SP1" in n for n in m.notes))


class CatalogueEntriesTest(unittest.TestCase):
    def test_arome_and_arpege_declared(self):
        sources, tasks, _ = load_catalogue()
        self.assertEqual(sources["arome-0025"].steps, tuple(range(52)))
        self.assertEqual(len(sources["arpege-01"].steps), 103)
        self.assertEqual(sources["arpege-01"].variables["sd"]["steps"], [[0, 48, 1], [51, 102, 3]])
        self.assertEqual(tasks["meteofrance-pnt"].crons, ("50 6 * * *", "50 12 * * *"))
        self.assertEqual(sources["arome-0025"].window_days, 7)


if __name__ == "__main__":
    unittest.main()
