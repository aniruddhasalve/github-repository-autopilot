from autopilot.report import markdown
from autopilot.rules import analyze


def test_detects_python_django_and_migration_risks():
    result = analyze(
        ["manage.py", "pyproject.toml", "README.md", "app/models.py"],
        ["app/migrations/0002_add.py", "app/views.py"],
    )
    assert "Python" in result.languages
    assert "Django" in result.frameworks
    codes = {finding.code for finding in result.findings}
    assert "RISK001" in codes
    assert "TEST001" in codes


def test_required_files_and_score_are_actionable():
    result = analyze(["app.py"], required=["README.md", "LICENSE"])
    assert result.score < 100
    output = markdown(result)
    assert "Missing README.md" in output
    assert "Health score" in output


def test_healthy_repository_has_no_risk_findings():
    result = analyze(
        ["pyproject.toml", "README.md", "LICENSE", "tests/test_app.py"],
        ["app.py", "tests/test_app.py"],
        required=["README.md", "LICENSE"],
    )
    assert result.score == 100
    assert not any(f.code.startswith("RISK") for f in result.findings)
