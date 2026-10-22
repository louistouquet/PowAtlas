import unittest
from datetime import datetime, timezone

import requests

from powatlas.http import HttpClient, HttpError, NotFound


class FakeResponse:
    def __init__(self, status, content=b"", headers=None):
        self.status_code = status
        self.content = content
        self.headers = headers or {}


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, headers=None, timeout=None):
        self.calls.append((url, dict(headers or {})))
        r = self.responses.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


class Clock:
    def __init__(self):
        self.t = 0.0
        self.sleeps = []

    def sleep(self, s):
        self.sleeps.append(s)
        self.t += s

    def now(self):
        return self.t


def client(responses, **kw):
    session = FakeSession(responses)
    clock = Clock()
    c = HttpClient(session=session, sleep=clock.sleep, monotonic=clock.now, retries=5, backoff=2.0,
                   max_backoff=300.0, timeout=60.0, **kw)
    return c, session, clock


SLOWDOWN = b"<?xml version='1.0'?><Error><Code>SlowDown</Code></Error>"


class HttpClientTest(unittest.TestCase):
    def test_retries_on_slowdown_then_succeeds(self):
        c, s, clock = client([FakeResponse(503, SLOWDOWN), FakeResponse(200, b"ok")], min_interval=0.0)
        r = c.get("https://x/y")
        self.assertEqual(r.content, b"ok")
        self.assertEqual(clock.sleeps, [2.0])

    def test_gives_up_after_retries(self):
        c, s, clock = client([FakeResponse(503, SLOWDOWN)] * 6, min_interval=0.0)
        with self.assertRaises(HttpError):
            c.get("https://x/y")
        self.assertEqual(clock.sleeps, [2.0, 4.0, 8.0, 16.0, 32.0])

    def test_connection_error_retried(self):
        c, s, clock = client([requests.ConnectionError("reset"), FakeResponse(200, b"ok")], min_interval=0.0)
        self.assertEqual(c.get("https://x").content, b"ok")

    def test_404_raises_not_found_without_retry(self):
        c, s, clock = client([FakeResponse(404)], min_interval=0.0)
        with self.assertRaises(NotFound):
            c.get("https://x/y")
        self.assertEqual(len(s.calls), 1)

    def test_403_is_an_error_without_retry(self):
        c, s, clock = client([FakeResponse(403)], min_interval=0.0)
        with self.assertRaises(HttpError):
            c.get("https://x/y")
        self.assertEqual(len(s.calls), 1)

    def test_range_answered_with_full_body_is_sliced(self):
        body = bytes(range(100))
        c, s, _ = client([FakeResponse(200, body)], min_interval=0.0)
        r = c.get("https://x", byte_range=(10, 19))
        self.assertEqual(r.content, body[10:20])
        self.assertEqual(s.calls[0][1]["Range"], "bytes=10-19")
        c, s, _ = client([FakeResponse(206, body[10:20])], min_interval=0.0)
        self.assertEqual(c.get("https://x", byte_range=(10, 19)).content, body[10:20])
        c, s, _ = client([FakeResponse(206, body[10:17])], min_interval=0.0)
        with self.assertRaises(HttpError):
            c.get("https://x", byte_range=(10, 19))
        c, s, _ = client([FakeResponse(200, body[:15])], min_interval=0.0)
        with self.assertRaises(HttpError):
            c.get("https://x", byte_range=(10, 19))

    def test_last_modified_parsed(self):
        c, s, _ = client([FakeResponse(200, b"x", {"Last-Modified": "Wed, 21 Oct 2026 06:30:15 GMT"})],
                         min_interval=0.0)
        r = c.get("https://x")
        self.assertEqual(r.last_modified, datetime(2026, 10, 21, 6, 30, 15, tzinfo=timezone.utc))
        c, s, _ = client([FakeResponse(200, b"x")], min_interval=0.0)
        self.assertIsNone(c.get("https://x").last_modified)

    def test_min_interval_spaces_requests(self):
        c, s, clock = client([FakeResponse(200, b"a"), FakeResponse(200, b"b")], min_interval=1.5)
        c.get("https://x")
        c.get("https://x")
        self.assertEqual(clock.sleeps, [1.5])

    def test_user_agent_identifies_project(self):
        c, s, _ = client([FakeResponse(200, b"a")], min_interval=0.0)
        c.get("https://x")
        self.assertTrue(s.calls[0][1]["User-Agent"].startswith("PowAtlas/0.1.0"))


if __name__ == "__main__":
    unittest.main()
