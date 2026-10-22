import json
import unittest

from fakes import FakeHttp
from powatlas.backfill import probe


class ProbeTest(unittest.TestCase):
    def test_probe_counts_requests_and_bytes(self):
        index = "\n".join(json.dumps({"param": p, "levtype": "sfc", "step": "24", "_offset": i * 10, "_length": 10})
                          for i, p in enumerate(("tp", "2t", "sf"))).encode()
        http = FakeHttp({"https://aws/x-24h-oper-fc.index": index, "https://aws/x-24h-oper-fc.grib2": bytes(30)})
        r = probe(http, ["https://aws/x-24h-oper-fc"], ranges_per_url=2, clock=iter([0.0, 4.0]).__next__)
        self.assertEqual((r.requests, r.bytes, r.seconds), (3, len(index) + 20, 4.0))

    def test_probe_counts_slowdowns(self):
        class CountingHttp(FakeHttp):
            retry_count = 0

            def get(self, url, byte_range=None):
                self.retry_count += 2  # two SlowDown answers absorbed by retries
                return super().get(url, byte_range)

        index = json.dumps({"param": "tp", "levtype": "sfc", "step": "0", "_offset": 0, "_length": 5}).encode()
        http = CountingHttp({"https://aws/y.index": index, "https://aws/y.grib2": bytes(5)})
        r = probe(http, ["https://aws/y"], ranges_per_url=1, clock=iter([0.0, 1.0]).__next__)
        self.assertEqual(r.slowdowns, 4)


if __name__ == "__main__":
    unittest.main()
