from .rules import Analysis


def markdown(analysis: Analysis) -> str:
    lines = [
        "## Repository Autopilot Report",
        "",
        f"**Health score: {analysis.score}/100**",
        "",
        f"Languages: {', '.join(sorted(analysis.languages)) or 'Unknown'}",
        f"Frameworks: {', '.join(sorted(analysis.frameworks)) or 'Unknown'}",
        "",
        "### Findings",
        "",
    ]
    if not analysis.findings:
        lines.append("No findings. Repository looks healthy.")
    for finding in analysis.findings:
        lines.append(f"- **{finding.level}** `{finding.code}` — {finding.title}: {finding.detail}")
        if finding.fix:
            lines.append(f"  - Fix: {finding.fix}")
    return "\n".join(lines)


def write_summary(body: str):
    import os

    path = os.getenv("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(body + "\n")
