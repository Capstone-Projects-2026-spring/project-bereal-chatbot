import importlib
import sys
from unittest.mock import Mock

import pytest


class DummyClient:
    def __init__(self, *args, **kwargs):
        pass

    def chat_postMessage(self, *args, **kwargs):
        return {"ts": "123.456", "channel": "C123"}


class DummyApp:
    def __init__(self, *args, **kwargs):
        pass

    def command(self, _name):
        def decorator(func):
            return func

        return decorator


@pytest.fixture
def bot_module(monkeypatch):
    import slack_bolt
    import slack_sdk

    monkeypatch.setenv("SLACK_TOKEN", "xoxb-test")
    monkeypatch.setenv("SLACK_APP_TOKEN", "xapp-test")

    monkeypatch.setattr(slack_sdk, "WebClient", DummyClient)
    monkeypatch.setattr(slack_bolt, "App", DummyApp)

    sys.modules.pop("bot", None)
    module = importlib.import_module("bot")
    return module


@pytest.mark.acceptance
def test_acceptance_user_sets_and_checks_prompt_time(bot_module):
    pick_ack = Mock()
    pick_respond = Mock()

    bot_module.pick_time(pick_ack, pick_respond, {"text": ""})
    pick_ack.assert_called_once()
    assert "Available time options" in pick_respond.call_args[0][0]

    pick_ack = Mock()
    pick_respond = Mock()

    bot_module.pick_time(pick_ack, pick_respond, {"text": "7"})
    pick_ack.assert_called_once()
    pick_respond.assert_called_once_with("Time set to: 03:00:00 PM")

    find_ack = Mock()
    find_respond = Mock()

    bot_module.handle_findtime_command(find_ack, find_respond)
    find_ack.assert_called_once()
    find_respond.assert_called_once_with("Today's random scheduled prompt time is 03:00:00 PM")
