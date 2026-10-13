import json
import os
from urllib import error, request


class GitHub:
    def __init__(self, token: str, repository: str):
        self.token, self.repository = token, repository
        self.base = f"https://api.github.com/repos/{repository}"

    def call(self, method: str, path: str, payload: dict | None = None):
        data = json.dumps(payload).encode() if payload is not None else None
        req = request.Request(
            self.base + path,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json",
            },
        )
        try:
            with request.urlopen(req, timeout=20) as response:
                return response.status, json.loads(response.read() or b"{}")
        except error.HTTPError as exc:
            return exc.code, {"error": exc.read().decode(errors="replace")}

    def comment(self, issue_number: int, body: str):
        return self.call("POST", f"/issues/{issue_number}/comments", {"body": body})

    def label(self, issue_number: int, labels: list[str]):
        return self.call("POST", f"/issues/{issue_number}/labels", {"labels": labels})

    def issue(self, title: str, body: str):
        return self.call("POST", "/issues", {"title": title, "body": body})


def enabled() -> bool:
    return bool(os.getenv("GITHUB_TOKEN") and os.getenv("GITHUB_REPOSITORY"))
