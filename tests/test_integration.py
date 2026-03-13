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
    
    def event(self, _name):
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
    return importlib.import_module("bot")


@pytest.mark.integration
def test_integration_randomtime_then_findtime(bot_module, monkeypatch):
    random_ack = Mock()
    random_respond = Mock()

    monkeypatch.setattr(bot_module.random, "randint", lambda _a, _b: 11)

    bot_module.random_time(random_ack, random_respond)

    random_ack.assert_called_once()
    random_respond.assert_called_once_with("New randomly selected daily target time: 05:00:00 PM")

    find_ack = Mock()
    find_respond = Mock()

    bot_module.handle_findtime_command(find_ack, find_respond)

    find_ack.assert_called_once()
    find_respond.assert_called_once_with("Today's random scheduled prompt time is 05:00:00 PM")
