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


def test_handle_findtime_command_ack_and_respond(bot_module):
    bot_module.daily_target_time = "02:00:00 PM"

    ack = Mock()
    respond = Mock()

    bot_module.handle_findtime_command(ack, respond)

    ack.assert_called_once()
    respond.assert_called_once_with("Today's random scheduled prompt time is 02:00:00 PM")


def test_pick_time_without_argument_shows_options(bot_module):
    ack = Mock()
    respond = Mock()

    bot_module.pick_time(ack, respond, {"text": ""})

    ack.assert_called_once()
    assert respond.call_count == 1
    assert "Available time options" in respond.call_args[0][0]


def test_pick_time_with_valid_choice_updates_global(bot_module):
    ack = Mock()
    respond = Mock()

    bot_module.pick_time(ack, respond, {"text": "5"})

    ack.assert_called_once()
    respond.assert_called_once_with("Time set to: 02:00:00 PM")
    assert bot_module.daily_target_time == "02:00:00 PM"


def test_pick_time_out_of_range(bot_module):
    ack = Mock()
    respond = Mock()

    bot_module.pick_time(ack, respond, {"text": "12"})

    ack.assert_called_once()
    respond.assert_called_once_with("Must pick a number between 1 and 11 to set the time.")


def test_pick_time_non_numeric(bot_module):
    ack = Mock()
    respond = Mock()

    bot_module.pick_time(ack, respond, {"text": "abc"})

    ack.assert_called_once()
    respond.assert_called_once_with("Please provide a valid number between 1 and 11 to set the time")


def test_random_time_sets_new_target(bot_module, monkeypatch):
    ack = Mock()
    respond = Mock()

    monkeypatch.setattr(bot_module.random, "randint", lambda _a, _b: 3)

    bot_module.random_time(ack, respond)

    ack.assert_called_once()
    respond.assert_called_once_with("New randomly selected daily target time: 01:00:00 PM")
    assert bot_module.daily_target_time == "01:00:00 PM"
