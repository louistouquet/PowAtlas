import json
import unittest
from datetime import datetime, timezone

from powatlas.github import GitHub


class FakeResp:
    def __init__(self, status, payload=None, content=b""):
        self.status_code = status
        self._payload = payload
        self.content = content if payload is None else json.dumps(payload).encode()
        self.text = self.content.decode(errors="replace")

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, routes):
        self.routes = routes  # list of (method, url-prefix, response) consumed in order
        self.calls = []

    def request(self, method, url, params=None, json=None, headers=None, timeout=None):
        self.calls.append((method, url, params, json, headers))
        for i, (m, prefix, resp) in enumerate(self.routes):
            if m == method and url.startswith(prefix):
                self.routes.pop(i)
                return resp
        raise AssertionError(f"unexpected {method} {url} {params}")


API = "https://api.github.com/repos/o/r"


class GitHubTest(unittest.TestCase):
    def test_list_artifact_names_paginates(self):
        page1 = {"artifacts": [{"id": i, "name": f"a{i}", "expired": False} for i in range(100)]}
        page2 = {"artifacts": [{"id": 100 + i, "name": f"b{i}", "expired": i == 0} for i in range(50)]}
        s = FakeSession([("GET", f"{API}/actions/artifacts", FakeResp(200, page1)),
                         ("GET", f"{API}/actions/artifacts", FakeResp(200, page2))])
        names = GitHub("o/r", "tok", session=s).list_artifact_names()
        self.assertEqual(len(names), 149)
        self.assertEqual(s.calls[1][2]["page"], 2)
        self.assertEqual(s.calls[0][4]["Authorization"], "Bearer tok")

    def test_issue_commented_when_open_issue_exists(self):
        s = FakeSession([
            ("GET", f"{API}/issues", FakeResp(200, [{"number": 7, "title": "Collecte : pertes du 2026-11-01"}])),
            ("POST", f"{API}/issues/7/comments", FakeResp(201, {})),
        ])
        GitHub("o/r", "tok", session=s).open_or_comment_issue("Collecte : pertes du 2026-11-01", "body", "collecte")
        self.assertEqual(s.calls[-1][3], {"body": "body"})

    def test_issue_opened_when_none_exists(self):
        s = FakeSession([("GET", f"{API}/issues", FakeResp(200, [])), ("POST", f"{API}/issues", FakeResp(201, {}))])
        GitHub("o/r", "tok", session=s).open_or_comment_issue("T", "body", "collecte")
        self.assertEqual(s.calls[-1][3], {"title": "T", "body": "body", "labels": ["collecte"]})

    def test_last_commit_date(self):
        s = FakeSession([("GET", f"{API}/commits", FakeResp(200, [{"commit": {"committer": {"date": "2026-10-22T08:31:30Z"}}}]))])
        self.assertEqual(GitHub("o/r", "tok", session=s).last_commit_date("main"),
                         datetime(2026, 10, 22, 8, 31, 30, tzinfo=timezone.utc))

    def test_http_error_raises(self):
        s = FakeSession([("GET", f"{API}/commits", FakeResp(403, {"message": "no"}))])
        with self.assertRaises(RuntimeError):
            GitHub("o/r", "tok", session=s).last_commit_date("main")


if __name__ == "__main__":
    unittest.main()
