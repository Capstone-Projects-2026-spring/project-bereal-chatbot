import pytest
from unittest.mock import Mock, patch
from commands.force_prompt_command import register_force_prompt_command
from commands.onboarding import register_onboarding
from commands.social_connector import find_matching_pair, register_social_connector_command, send_social_connector_message
from commands.set_channel_command import register_set_channel_command
from bot.state import create_state, StateManager


class DummyApp:
    def __init__(self):
        self._commands = {}
        self._actions = {}
        self._views = {}
        self._events = {}

    def command(self, name):
        def decorator(func):
            self._commands[name] = func
            return func
        return decorator

    def action(self, name):
        def decorator(func):
            self._actions[name] = func
            return func
        return decorator

    def view(self, name):
        def decorator(func):
            self._views[name] = func
            return func
        return decorator

    def event(self, name):
        def decorator(func):
            self._events[name] = func
            return func
        return decorator

    def get_command(self, name):
        return self._commands[name]

    def get_action(self, name):
        return self._actions[name]

    def get_view(self, name):
        return self._views[name]


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

    with patch("commands.force_prompt_command.get_random_prompt_text", return_value=("1", "How are you?", [])), \
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

    with patch("commands.force_prompt_command.get_random_prompt_text", return_value=("1", "How are you?", [])), \
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

    with patch("commands.force_prompt_command.get_random_prompt_text", return_value=("1", "How are you?", [])), \
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


def test_picktags_command_opens_static_checkbox_modal(app, state_manager):
    register_onboarding(app, state_manager)
    handler = app.get_command("/picktags")

    ack = Mock()
    client = Mock()

    with patch("commands.onboarding.get_user_interests", return_value=["food", "work_life"]):
        handler(
            ack=ack,
            body={"team_id": "T123", "user_id": "U123", "trigger_id": "trigger-1"},
            client=client,
        )

    ack.assert_called_once()
    client.views_open.assert_called_once()

    view = client.views_open.call_args.kwargs["view"]
    element = view["blocks"][1]["element"]
    assert element["type"] == "checkboxes"
    assert [option["value"] for option in element["options"]] == [
        "sports",
        "food",
        "hobbies",
        "personal_life",
        "tv_movies",
        "work_life",
        "would_you_rather",
    ]
    assert [option["value"] for option in element["initial_options"]] == ["food", "work_life"]


def test_picktags_submission_saves_selected_tags(app, state_manager):
    register_onboarding(app, state_manager)
    handler = app.get_view("user_interests_modal")

    ack = Mock()
    client = Mock()

    body = {
        "user": {"id": "U123"},
        "view": {
            "private_metadata": "T123|U123",
            "state": {
                "values": {
                    "interests_block": {
                        "selected_interests": {
                            "selected_options": [
                                {"value": "sports"},
                                {"value": "food"},
                            ]
                        }
                    }
                }
            },
        },
    }

    with patch("commands.onboarding.save_user_interests") as save_user_interests:
        handler(ack=ack, body=body, client=client)

    ack.assert_called_once()
    save_user_interests.assert_called_once_with("T123", "U123", ["sports", "food"])
    client.chat_postMessage.assert_called_once()


def test_social_connector_finds_pair_from_shared_tags():
    fake_users = [
        {"user_id": "U1", "tags": ["food", "sports"]},
        {"user_id": "U2", "tags": ["food", "hobbies"]},
        {"user_id": "U3", "tags": ["tv_movies"]},
    ]

    with patch("services.mongo_service.get_all_user_interests", return_value=fake_users), \
         patch("commands.social_connector.random.choice", side_effect=lambda pairs: pairs[0]):
        user1_id, user2_id, shared_tags = find_matching_pair("T123")

    assert (user1_id, user2_id) == ("U1", "U2")
    assert shared_tags == ["food"]


def test_social_connector_randomly_selects_from_all_matching_pairs():
    fake_users = [
        {"user_id": "U1", "tags": ["food", "sports"]},
        {"user_id": "U2", "tags": ["food"]},
        {"user_id": "U3", "tags": ["sports"]},
    ]

    with patch("services.mongo_service.get_all_user_interests", return_value=fake_users), \
         patch("commands.social_connector.random.choice", side_effect=lambda pairs: pairs[-1]):
        user1_id, user2_id, shared_tags = find_matching_pair("T123")

    assert (user1_id, user2_id) == ("U1", "U3")
    assert shared_tags == ["sports"]


def test_social_connector_posts_soft_intro_message():
    client = Mock()

    with patch("commands.social_connector.find_matching_pair", return_value=("U1", "U2", ["food"])), \
         patch("services.llm_service.get_social_connector_message", return_value="hey I saw you both mentioned food"), \
         patch("services.llm_service.get_social_connector_icebreaker", return_value="what's a favorite food you both love?"):
        posted = send_social_connector_message(client, channel="C123", team_id="T123")

    assert posted is True
    assert client.chat_postMessage.call_count == 2
    assert client.chat_postMessage.call_args_list[0].kwargs == {"channel": "C123", "text": "hey I saw you both mentioned food"}
    assert client.chat_postMessage.call_args_list[1].kwargs == {"channel": "C123", "text": "what's a favorite food you both love?"}


def test_social_connector_command_posts_in_current_channel(app):
    register_social_connector_command(app)
    handler = app.get_command("/connect")

    ack = Mock()
    respond = Mock()
    client = Mock()

    with patch("commands.social_connector.send_social_connector_message", return_value=True) as send_social:
        handler(
            ack=ack,
            respond=respond,
            body={"channel_id": "C123", "team_id": "T123"},
            client=client,
        )

    ack.assert_called_once()
    send_social.assert_called_once_with(client, "C123", "T123")
    respond.assert_called_once_with("Posted a social connector intro in this channel.")
