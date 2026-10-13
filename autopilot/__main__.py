import argparse
import json
import os
from pathlib import Path

import yaml

from .github import GitHub, enabled
from .report import markdown, write_summary
from .rules import analyze


def event_payload():
    path = os.getenv("GITHUB_EVENT_PATH")
    return json.loads(Path(path).read_text()) if path and Path(path).exists() else {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["report", "enforce", "pull_request"], default="report")
    parser.add_argument("--config", default=".github/repository-autopilot.yml")
    parser.add_argument("--fail-under", type=int, default=0)
    args = parser.parse_args()
    config = {}
    if Path(args.config).exists():
        config = yaml.safe_load(Path(args.config).read_text()) or {}
    files = [p for p in os.getenv("AUTOPILOT_FILES", "").splitlines() if p] or [
        str(p) for p in Path(".").rglob("*") if p.is_file() and ".git" not in p.parts
    ]
    event = event_payload()
    changed = [
        f["filename"]
        for f in event.get("pull_request", {}).get("files", [])
        if isinstance(f, dict) and "filename" in f
    ]
    analysis = analyze(files, changed, config.get("files", {}).get("required"))
    body = markdown(analysis)
    print(body)
    write_summary(body)
    if enabled() and args.mode in {"pull_request", "enforce"}:
        gh = GitHub(os.environ["GITHUB_TOKEN"], os.environ["GITHUB_REPOSITORY"])
        number = event.get("pull_request", {}).get("number") or event.get("issue", {}).get("number")
        labels = [
            "autopilot",
            "high-risk"
            if analysis.score < 70
            else "needs-review"
            if analysis.score < 90
            else "healthy",
        ]
        if number:
            gh.label(number, labels)
            gh.comment(number, body)
        elif config.get("maintenance", {}).get("create_weekly_report"):
            gh.issue("Repository Autopilot maintenance report", body)
    return 0 if analysis.score >= args.fail_under else 1


if __name__ == "__main__":
    raise SystemExit(main())
