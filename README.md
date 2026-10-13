# GitHub Repository Autopilot

> A zero-configuration Docker GitHub Action that audits, labels, and reports on repository health directly inside GitHub.

Repository Autopilot turns routine maintainer work into GitHub-native output: step summaries, PR comments, labels, and scheduled maintenance issues.

## Use it in a repository

Copy the workflow from `examples/autopilot-workflow.yml` into `.github/workflows/autopilot.yml`:

```yaml
name: Repository Autopilot
on:
  pull_request:
  schedule:
    - cron: '0 9 * * 1'
permissions:
  contents: read
  issues: write
  pull-requests: write
jobs:
  autopilot:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aniruddhasalve/github-repository-autopilot@v1
        with:
          mode: pull_request
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Add optional configuration at `.github/repository-autopilot.yml`:

```yaml
version: 1
files:
  required: [README.md, LICENSE, CONTRIBUTING.md, SECURITY.md]
maintenance:
  create_weekly_report: true
```

## What it does today

- Detects languages and frameworks
- Checks for dependency metadata
- Checks required repository files
- Detects migration changes in pull requests
- Detects security-sensitive file changes
- Detects Python changes without tests
- Calculates a simple health score
- Writes a GitHub Actions step summary
- Adds labels and comments in report/enforce/pull-request modes
- Creates a scheduled maintenance issue when configured

## Modes

- `report`: summary only; safest default
- `enforce`: fail below `fail-under`
- `pull_request`: add labels and a report comment to the PR

The action is intentionally conservative: it reports findings and creates comments/issues, but does not modify source files or open fix PRs yet.

## Local development

```bash
pip install -e '.[dev]'
ruff check .
pytest -q
AUTOPILOT_FILES=$'README.md\npyproject.toml\napp/models.py' python -m autopilot --mode report
```

## Security model

The action uses the workflow's `GITHUB_TOKEN`. Grant only the permissions required by the mode. `report` needs no write permissions. Never add a personal access token to a repository workflow. All automated write operations are explicit and limited to labels, comments, and scheduled issue creation.

## Roadmap

- GitHub check-run annotations
- Dependabot and Actions version checks
- Secret-pattern reporting without exposing values
- Safe maintenance pull requests
- CODEOWNERS-aware reviewer suggestions
- Duplicate issue similarity hints

MIT licensed. Contributions welcome.
