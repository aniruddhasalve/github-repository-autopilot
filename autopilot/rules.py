from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Finding:
    code: str
    level: str
    title: str
    detail: str
    fix: str = ""


@dataclass
class Analysis:
    files: list[str]
    findings: list[Finding] = field(default_factory=list)
    languages: set[str] = field(default_factory=set)
    frameworks: set[str] = field(default_factory=set)

    @property
    def score(self) -> int:
        penalty = sum(
            25 if f.level == "FAIL" else 10 if f.level == "WARN" else 0 for f in self.findings
        )
        return max(0, 100 - min(100, penalty))


def analyze(
    files: list[str], changed_files: list[str] | None = None, required: list[str] | None = None
) -> Analysis:
    names = {Path(f).name.lower() for f in files}
    lower = [f.lower() for f in files]
    result = Analysis(files=files)
    if any(f.endswith(".py") for f in lower):
        result.languages.add("Python")
    if any(f.endswith((".js", ".ts", ".tsx")) for f in lower):
        result.languages.add("JavaScript/TypeScript")
    if "manage.py" in names or any("django" in f for f in lower):
        result.frameworks.add("Django")
    if any("fastapi" in f for f in lower):
        result.frameworks.add("FastAPI")
    if any("requirements" in f or "pyproject.toml" in f for f in lower):
        result.findings.append(
            Finding(
                "DEP001",
                "PASS",
                "Dependency metadata found",
                "The repository declares Python dependencies.",
            )
        )
    else:
        result.findings.append(
            Finding(
                "DEP001",
                "WARN",
                "Dependency metadata missing",
                "No requirements file or pyproject.toml detected.",
                "Add pyproject.toml or requirements.txt.",
            )
        )
    required = required or ["README.md", "LICENSE"]
    for item in required:
        if item not in files:
            result.findings.append(
                Finding(
                    "FILE001",
                    "WARN",
                    f"Missing {item}",
                    f"Required repository file {item} was not found.",
                    f"Add {item} to the repository.",
                )
            )
    if changed_files:
        changed = [f.lower() for f in changed_files]
        if any("migration" in f for f in changed):
            result.findings.append(
                Finding(
                    "RISK001",
                    "WARN",
                    "Database migration changed",
                    "Review migration safety before merging.",
                    "Test against production-sized data.",
                )
            )
        if any("auth" in f or "permission" in f or "security" in f for f in changed):
            result.findings.append(
                Finding(
                    "RISK002",
                    "WARN",
                    "Security-sensitive code changed",
                    "Authentication or authorization files changed.",
                    "Request a security-focused review.",
                )
            )
        if any(f.endswith(".py") for f in changed) and not any("test" in f for f in changed):
            result.findings.append(
                Finding(
                    "TEST001",
                    "WARN",
                    "Python changed without tests",
                    "The pull request changes Python but no test file.",
                    "Add or update tests for the changed behavior.",
                )
            )
    return result
