"""Minimal GitHub REST client: artifacts (state of the collection), issues, commits."""

from datetime import datetime, timezone

import requests

API = "https://api.github.com"


class GitHub:
    def __init__(self, repo: str, token: str, session: requests.Session | None = None, timeout: float = 60.0):
        if not repo or "/" not in repo:
            raise ValueError(f"repository must be owner/name, got {repo!r}")
        if not token:
            raise ValueError("a GitHub token is required")
        self.repo = repo
        self.session = session if session is not None else requests.Session()
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _call(self, method: str, path: str, params=None, json=None):
        url = f"{API}/repos/{self.repo}{path}"
        r = self.session.request(method, url, params=params, json=json, headers=self.headers, timeout=self.timeout)
        if r.status_code not in (200, 201):
            raise RuntimeError(f"GitHub {method} {path}: HTTP {r.status_code} {r.text[:200]}")
        return r

    def list_artifacts(self) -> list[dict]:
        """All non-expired artifacts of the repository (pages of 100)."""
        out, page = [], 1
        while True:
            batch = self._call("GET", "/actions/artifacts", params={"per_page": 100, "page": page}).json()["artifacts"]
            out.extend(a for a in batch if not a.get("expired"))
            if len(batch) < 100:
                return out
            page += 1

    def list_artifact_names(self) -> list[str]:
        return [a["name"] for a in self.list_artifacts()]

    def download_artifact(self, artifact_id: int) -> bytes:
        """Zip archive of an artifact (the API redirects to a short-lived link)."""
        return self._call("GET", f"/actions/artifacts/{artifact_id}/zip").content

    def open_or_comment_issue(self, title: str, body: str, label: str) -> None:
        issues = self._call("GET", "/issues", params={"state": "open", "labels": label, "per_page": 100}).json()
        for issue in issues:
            if issue["title"] == title:
                self._call("POST", f"/issues/{issue['number']}/comments", json={"body": body})
                return
        self._call("POST", "/issues", json={"title": title, "body": body, "labels": [label]})

    def last_commit_date(self, branch: str) -> datetime:
        commits = self._call("GET", "/commits", params={"sha": branch, "per_page": 1}).json()
        date = commits[0]["commit"]["committer"]["date"]
        return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
