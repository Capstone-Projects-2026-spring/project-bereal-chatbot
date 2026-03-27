import pytest
from unittest.mock import Mock, patch
from commands.force_prompt_command import register_force_prompt_command
from commands.set_channel_command import register_set_channel_command
from bot.state import create_state, StateManager


class DummyApp:
    def __init__(self):
        self._commands = {}

    def command(self, name):
        def decorator(func):
            self._commands[name] = func
            return func
        return decorator

    def get_command(self, name):
        return self._commands[name]


@pytest.fixture
def app():
    return DummyApp()


@pytest.fixture
def state():
    return create_state(default_channel="#bot-test")


@pytest.fixture
def state_manager():
    return StateManager()


def test_forceprompt_acks(app):
    register_force_prompt_command(app)
    handler = app.get_command("/forceprompt")

    ack = Mock()
    respond = Mock()
    client = Mock()
    client.chat_postMessage.return_value = {"ok": True}

    with patch("commands.force_prompt_command.get_random_prompt_text", return_value=("1", "How are you?")), \
         patch("commands.force_prompt_command.mark_prompt_asked"):
        handler(ack=ack, respond=respond, body={"text": "", "channel_id": "C123"}, client=client)

    ack.assert_called_once()


def test_forceprompt_posts_to_command_channel(app):
    register_force_prompt_command(app)
    handler = app.get_command("/forceprompt")

    ack = Mock()
    respond = Mock()
    client = Mock()
    client.chat_postMessage.return_value = {"ok": True}

    with patch("commands.force_prompt_command.get_random_prompt_text", return_value=("1", "How are you?")), \
         patch("commands.force_prompt_command.mark_prompt_asked"):
        handler(ack=ack, respond=respond, body={"text": "", "channel_id": "C123"}, client=client)

    client.chat_postMessage.assert_called_once()
    assert client.chat_postMessage.call_args[1]["channel"] == "C123"


def test_forceprompt_posts_to_specified_channel(app):
    register_force_prompt_command(app)
    handler = app.get_command("/forceprompt")

    ack = Mock()
    respond = Mock()
    client = Mock()
    client.chat_postMessage.return_value = {"ok": True}

    with patch("commands.force_prompt_command.get_random_prompt_text", return_value=("1", "How are you?")), \
         patch("commands.force_prompt_command.mark_prompt_asked"):
        handler(ack=ack, respond=respond, body={"text": "#general", "channel_id": "C123"}, client=client)

    assert client.chat_postMessage.call_args[1]["channel"] == "#general"


def test_setchannel_updates_state(app, state_manager):
    register_set_channel_command(app, state_manager)
    handler = app.get_command("/setchannel")

    ack = Mock()
    respond = Mock()
    client = Mock()
    client.chat_postMessage.return_value = {"ok": True}

    handler(ack=ack, respond=respond, body={"text": "#new-channel", "team_id": "T123"}, client=client)

    ack.assert_called_once()
    assert state_manager.get_state("T123").get_active_channel() == "#new-channel"


def test_setchannel_rejects_missing_channel(app, state_manager):
    register_set_channel_command(app, state_manager)
    handler = app.get_command("/setchannel")

    ack = Mock()
    respond = Mock()
    client = Mock()

    handler(ack=ack, respond=respond, body={"text": "", "team_id": "T123"}, client=client)

    ack.assert_called_once()
    respond.assert_called_once()
    assert state_manager.get_state("T123").get_active_channel() != "#new-channel"
