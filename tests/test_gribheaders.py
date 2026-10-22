import unittest

import eccodes

from fakes import FakeHttp
from gribfactory import make_message
from powatlas.gribheaders import HeaderInfo, coalesce, parse_header, walk_messages


def eccodes_identity(msg):
    """Reference values read by eccodes itself."""
    h = eccodes.codes_new_from_message(msg)
    try:
        keys = ("discipline", "parameterCategory", "parameterNumber", "productDefinitionTemplateNumber")
        return tuple(eccodes.codes_get_long(h, k) for k in keys) + (eccodes.codes_get_long(h, "typeOfFirstFixedSurface"),)
    finally:
        eccodes.codes_release(h)


class ParseHeaderTest(unittest.TestCase):
    def test_parse_header_accumulation_template_4_8(self):
        msg = make_message("tp", step_range="0-24")
        h = parse_header(msg, 0)
        self.assertEqual((h.discipline, h.category, h.number, h.template, h.level_type), eccodes_identity(msg))
        self.assertEqual((h.offset, h.length, h.template, h.level_value), (0, len(msg), 8, None))

    def test_parse_header_instant_at_two_metres(self):
        msg = make_message("2t", step_range="6", type_of_level="heightAboveGround", level=2)
        h = parse_header(msg, 0)
        self.assertEqual((h.discipline, h.category, h.number, h.level_type, h.level_value, h.template),
                         (0, 0, 0, 103, 2.0, 0))

    def test_short_buffer_raises(self):
        with self.assertRaises(ValueError):
            parse_header(make_message()[:40], 0)
        with self.assertRaises(ValueError):
            parse_header(b"<html>", 0)


class WalkTest(unittest.TestCase):
    def test_walk_messages_offsets(self):
        msgs = [make_message("tp"), make_message("2t", step_range="1", type_of_level="heightAboveGround", level=2),
                make_message("tp", step_range="0-2")]
        data = b"".join(msgs)
        http = FakeHttp({"https://x/f.grib2": data})
        heads = walk_messages(http, "https://x/f.grib2", len(data), head_bytes=1024)
        self.assertEqual([h.offset for h in heads], [0, len(msgs[0]), len(msgs[0]) + len(msgs[1])])
        self.assertEqual([h.length for h in heads], [len(m) for m in msgs])
        self.assertEqual([h.number for h in heads], [eccodes_identity(m)[2] for m in msgs])
        self.assertEqual(len(http.requests), 3)

    def test_walk_detects_size_mismatch(self):
        data = make_message()
        http = FakeHttp({"https://x/f.grib2": data})
        with self.assertRaises(ValueError):
            walk_messages(http, "https://x/f.grib2", len(data) + 10, head_bytes=1024)


class CoalesceTest(unittest.TestCase):
    def test_coalesce_contiguous(self):
        self.assertEqual(coalesce([(10, 19), (0, 9), (30, 39), (20, 25)]), [(0, 25), (30, 39)])
        self.assertEqual(coalesce([]), [])

    def test_coalesce_rejects_overlap(self):
        with self.assertRaises(ValueError):
            coalesce([(0, 10), (5, 20)])


if __name__ == "__main__":
    unittest.main()
