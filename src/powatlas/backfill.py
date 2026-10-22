"""Historical backfill from the AWS copies (run on the pilot's PC).

``probe`` measures the sustained request rate first: the AWS bucket of ECMWF
answered ``SlowDown`` from the cloud session (spec, section 2), so the
feasibility of the ~386 000 range requests is measured before committing to them.
"""

import time
from collections.abc import Callable
from dataclasses import dataclass

from powatlas.http import HttpClient
from powatlas.indexes import parse_ecmwf_index


@dataclass(frozen=True)
class ProbeResult:
    requests: int
    seconds: float
    slowdowns: int  # retries absorbed by the client (SlowDown, 429, 5xx, cut connections)
    bytes: int


def probe(http: HttpClient, urls: list[str], ranges_per_url: int, clock: Callable[[], float] = time.monotonic) -> ProbeResult:
    """Read the index of each ECMWF step file (path without extension) and its first ranges."""
    t0 = clock()
    retries0 = http.retry_count
    requests = size = 0
    for url in urls:
        index = http.get(url + ".index").content
        requests += 1
        size += len(index)
        for e in parse_ecmwf_index(index)[:ranges_per_url]:
            size += len(http.get(url + ".grib2", byte_range=(e.offset, e.offset + e.length - 1)).content)
            requests += 1
    return ProbeResult(requests, clock() - t0, http.retry_count - retries0, size)
