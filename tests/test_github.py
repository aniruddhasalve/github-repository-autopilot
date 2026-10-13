import json
from unittest.mock import patch

from autopilot.github import GitHub


def test_github_actions_use_expected_payloads():
    client = GitHub("token", "owner/repo")
    with patch("autopilot.github.request.urlopen") as open_url:
        response = open_url.return_value.__enter__.return_value
        response.status = 200
        response.read.return_value = b"{}"
        client.label(7, ["autopilot"])
        req = open_url.call_args.args[0]
        assert req.full_url.endswith("/issues/7/labels")
        assert json.loads(req.data) == {"labels": ["autopilot"]}
