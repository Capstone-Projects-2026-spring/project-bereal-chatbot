import os
import pytest


REQUIRED_ENV_VARS = [
    "SLACK_BOT_TOKEN",
    "SLACK_APP_TOKEN",
    "SLACK_SIGNING_SECRET",
    "SLACK_CLIENT_ID",
    "SLACK_CLIENT_SECRET",
    "SLACK_REDIRECT_URI",
    "MONGO_URI",
]


@pytest.mark.parametrize("var", REQUIRED_ENV_VARS)
def test_required_env_var_is_set(var, monkeypatch):
    monkeypatch.setenv(var, "dummy-value")
    assert os.getenv(var) is not None


def test_slack_bot_token_format(monkeypatch):
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test-token")
    assert os.getenv("SLACK_BOT_TOKEN").startswith("xoxb-")


def test_slack_app_token_format(monkeypatch):
    monkeypatch.setenv("SLACK_APP_TOKEN", "xapp-test-token")
    assert os.getenv("SLACK_APP_TOKEN").startswith("xapp-")
