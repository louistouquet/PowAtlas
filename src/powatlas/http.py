"""HTTP GET with retries, polite pacing and byte ranges.

Retries cover transient conditions only (connection errors, 429, 5xx including
the S3 ``SlowDown`` answer). Any other status fails immediately, so that an
access change at a producer is noticed instead of being retried for hours.
"""

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import requests

from powatlas import __version__

USER_AGENT = f"PowAtlas/{__version__} (+https://github.com/louistouquet/PowAtlas)"
RETRY_STATUS = frozenset({429, 500, 502, 503, 504})


class HttpError(RuntimeError):
    """A request failed for good; ``status`` is the HTTP status when there was one."""

    def __init__(self, message: str, status: int | None = None) -> None:
        super().__init__(message)
        self.status = status


class NotFound(HttpError):
    """HTTP 404: the resource does not exist (yet, or any more)."""


# Response headers kept for traceability (cache state, identity of the copy).
KEPT_HEADERS = ("Date", "ETag", "Age", "Cache-Control", "Content-Encoding", "Last-Modified")


@dataclass(frozen=True)
class Response:
    status: int
    content: bytes
    last_modified: datetime | None
    url: str
    headers: dict = field(default_factory=dict)


def _last_modified(headers) -> datetime | None:
    """Producer's Last-Modified in UTC; None if absent or unreadable (recorded as such by the writer)."""
    value = headers.get("Last-Modified")
    if not value:
        return None
    try:
        t = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    # HTTP dates are GMT; "-0000" yields a naive datetime that must not be read as local time.
    if t.tzinfo is None:
        return t.replace(tzinfo=timezone.utc)
    return t.astimezone(timezone.utc)


class HttpClient:
    def __init__(
        self,
        retries: int,
        backoff: float,
        max_backoff: float,
        min_interval: float,
        timeout: float,
        session: requests.Session | None = None,
        sleep: Callable[[float], None] = time.sleep,
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        self.retries = retries
        self.backoff = backoff
        self.max_backoff = max_backoff
        self.min_interval = min_interval
        self.timeout = timeout
        self.session = session if session is not None else requests.Session()
        self._sleep = sleep
        self._monotonic = monotonic
        self._last_request: float | None = None

    def _pace(self) -> None:
        if self._last_request is not None and self.min_interval > 0:
            wait = self.min_interval - (self._monotonic() - self._last_request)
            if wait > 0:
                self._sleep(wait)
        self._last_request = self._monotonic()

    def get(self, url: str, byte_range: tuple[int, int] | None = None) -> Response:
        """GET ``url``; ``byte_range`` is an inclusive (first, last) byte pair."""
        headers = {"User-Agent": USER_AGENT}
        if byte_range is not None:
            first, last = byte_range
            if first < 0 or last < first:
                raise ValueError(f"bad byte range {byte_range}")
            headers["Range"] = f"bytes={first}-{last}"
        delay = self.backoff
        last_problem = ""
        for attempt in range(self.retries + 1):
            if attempt:
                self._sleep(delay)
                delay = min(delay * 2, self.max_backoff)
            self._pace()
            try:
                r = self.session.get(url, headers=headers, timeout=self.timeout)
            except (
                requests.ConnectionError,
                requests.Timeout,
                requests.exceptions.ChunkedEncodingError,
                requests.exceptions.ContentDecodingError,
            ) as exc:
                # Transient: connection reset, timeout, body cut during the transfer.
                last_problem = f"{type(exc).__name__}: {exc}"
                continue
            except requests.RequestException as exc:
                raise HttpError(f"{url}: {type(exc).__name__}: {exc}") from exc
            if r.status_code in RETRY_STATUS:
                last_problem = f"HTTP {r.status_code}"
                continue
            if r.status_code == 404:
                raise NotFound(f"HTTP 404 for {url}", status=404)
            if r.status_code not in (200, 206):
                raise HttpError(f"HTTP {r.status_code} for {url}", status=r.status_code)
            content = r.content
            if byte_range is not None:
                content = self._range_content(url, r.status_code, content, byte_range)
            kept = {k: r.headers[k] for k in KEPT_HEADERS if k in r.headers}
            return Response(r.status_code, content, _last_modified(r.headers), url, kept)
        raise HttpError(f"{url}: gave up after {self.retries + 1} attempts ({last_problem})")

    @staticmethod
    def _range_content(url: str, status: int, content: bytes, byte_range: tuple[int, int]) -> bytes:
        first, last = byte_range
        size = last - first + 1
        if status == 206:
            if len(content) != size:
                raise HttpError(f"{url}: range {byte_range} returned {len(content)} bytes")
            return content
        # Some proxies ignore Range and send the whole body with 200.
        if len(content) <= last:
            raise HttpError(f"{url}: full body of {len(content)} bytes shorter than range {byte_range}")
        return content[first : last + 1]
