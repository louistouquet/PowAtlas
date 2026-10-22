"""Test doubles shared by adapter tests."""

from datetime import datetime, timezone

from powatlas.http import NotFound, Response

LAST_MODIFIED = datetime(2026, 11, 1, 1, 4, tzinfo=timezone.utc)


class FakeHttp:
    """Serves bytes by URL; unknown URLs raise NotFound. Records every request."""

    def __init__(self, files: dict[str, bytes], last_modified=LAST_MODIFIED):
        self.files = files
        self.last_modified = last_modified
        self.requests = []

    def get(self, url, byte_range=None):
        self.requests.append((url, byte_range))
        if url not in self.files:
            raise NotFound(url)
        data = self.files[url]
        if byte_range is not None:
            data = data[byte_range[0] : byte_range[1] + 1]
        return Response(206 if byte_range else 200, data, self.last_modified, url)
