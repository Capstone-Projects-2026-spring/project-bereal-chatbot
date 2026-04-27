import pytest
from unittest.mock import Mock, patch
from commands.force_prompt_command import register_force_prompt_command
from commands.onboarding import register_onboarding
from commands.social_connector import find_matching_pair, register_social_connector_command, send_social_connector_message
from commands.set_channel_command import register_set_channel_command
from commands.prompt_stats_command import register_prompt_stats_command
from commands.pick_topic_command import register_pick_topic_command
from commands.time_commands import register_time_commands
from commands.status_command import register_status_command
from commands.help_command import register_help_command
from services.streak_service import register_streak_command
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
    respond.assert_not_called()


def test_social_connector_command_responds_when_no_match_found(app):
    register_social_connector_command(app)
    handler = app.get_command("/connect")

    ack = Mock()
    respond = Mock()
    client = Mock()

    with patch("commands.social_connector.send_social_connector_message", return_value=False) as send_social:
        handler(
            ack=ack,
            respond=respond,
            body={"channel_id": "C123", "team_id": "T123"},
            client=client,
        )

    ack.assert_called_once()
    send_social.assert_called_once_with(client, "C123", "T123")
    respond.assert_called_once_with("No matching pair found yet. Have a few people set their tags with `/picktags` and try again.")


def test_promptstats_returns_sorted_summary(app):
    register_prompt_stats_command(app)
    handler = app.get_command("/promptstats")

    ack = Mock()
    respond = Mock()
    tracker = Mock()
    tracker.get_all_stats.return_value = [
        {
            "tags": ["food", "hobbies"],
            "times_asked": 3,
            "times_responded": 2,
            "prompt": "What did you eat today?",
        }
    ]

    with patch("commands.prompt_stats_command.get_tracker", return_value=tracker):
        handler(ack=ack, respond=respond, body={"team_id": "T123"})

    ack.assert_called_once()
    tracker.get_all_stats.assert_called_once_with("T123")
    respond.assert_called_once()
    assert "*Prompt Stats (most asked first)*" in respond.call_args.args[0]
    assert "asked 3x" in respond.call_args.args[0]


def test_promptstats_handles_empty_data(app):
    register_prompt_stats_command(app)
    handler = app.get_command("/promptstats")

    ack = Mock()
    respond = Mock()
    tracker = Mock()
    tracker.get_all_stats.return_value = []

    with patch("commands.prompt_stats_command.get_tracker", return_value=tracker):
        handler(ack=ack, respond=respond, body={"team_id": "T123"})

    ack.assert_called_once()
    respond.assert_called_once_with("No prompt stats recorded yet.")


def test_picktopic_lists_topics_when_no_arg(app, state_manager):
    register_pick_topic_command(app, state_manager)
    handler = app.get_command("/picktopic")

    ack = Mock()
    respond = Mock()

    with patch("commands.pick_topic_command.get_available_topics", return_value=["food", "sports"]):
        handler(ack=ack, respond=respond, body={"text": "", "team_id": "T123"})

    ack.assert_called_once()
    respond.assert_called_once()
    text = respond.call_args.args[0]
    assert "*Available topics:*" in text
    assert "`food`" in text
    assert "`sports`" in text


def test_picktopic_sets_pending_topic_when_valid(app, state_manager):
    register_pick_topic_command(app, state_manager)
    handler = app.get_command("/picktopic")

    ack = Mock()
    respond = Mock()

    with patch("commands.pick_topic_command.get_available_topics", return_value=["food", "sports"]):
        handler(ack=ack, respond=respond, body={"text": "food", "team_id": "T123"})

    ack.assert_called_once()
    respond.assert_called_once_with("Topic set, the next prompt will be from the `food` topic.")
    assert state_manager.get_state("T123").get_and_clear_pending_topic() == "food"


def test_picktopic_rejects_unknown_topic(app, state_manager):
    register_pick_topic_command(app, state_manager)
    handler = app.get_command("/picktopic")

    ack = Mock()
    respond = Mock()

    with patch("commands.pick_topic_command.get_available_topics", return_value=["food", "sports"]):
        handler(ack=ack, respond=respond, body={"text": "music", "team_id": "T123"})

    ack.assert_called_once()
    respond.assert_called_once()
    assert "Unknown topic `music`" in respond.call_args.args[0]


def test_findtime_returns_target_time_and_mode(app, state_manager):
    register_time_commands(app, state_manager)
    handler = app.get_command("/findtime")

    ack = Mock()
    respond = Mock()
    state_manager.get_state("T123").set_selected_mode("mode_random")

    with patch("commands.time_commands._get_target_time", return_value="02:00:00 PM"):
        handler(ack=ack, respond=respond, body={"team_id": "T123"})

    ack.assert_called_once()
    respond.assert_called_once_with("Scheduled prompt time: *02:00:00 PM* (mode: `mode_random`)")


def test_picktime_lists_options_when_empty(app, state_manager):
    register_time_commands(app, state_manager)
    handler = app.get_command("/picktime")

    ack = Mock()
    respond = Mock()

    handler(ack=ack, respond=respond, body={"team_id": "T123", "text": ""})

    ack.assert_called_once()
    respond.assert_called_once()
    assert "Available time options:" in respond.call_args.args[0]
    assert "Use `/picktime <number>`" in respond.call_args.args[0]


def test_picktime_sets_target_time_for_valid_choice(app, state_manager):
    register_time_commands(app, state_manager)
    handler = app.get_command("/picktime")

    ack = Mock()
    respond = Mock()

    with patch("commands.time_commands.preSet_time_library", return_value="02:00:00 PM"):
        handler(ack=ack, respond=respond, body={"team_id": "T123", "text": "5"})

    ack.assert_called_once()
    respond.assert_called_once_with("Time set to: 02:00:00 PM")
    assert state_manager.get_state("T123").get_daily_target_time() == "02:00:00 PM"


def test_picktime_rejects_invalid_input(app, state_manager):
    register_time_commands(app, state_manager)
    handler = app.get_command("/picktime")

    ack = Mock()
    respond = Mock()

    handler(ack=ack, respond=respond, body={"team_id": "T123", "text": "abc"})

    ack.assert_called_once()
    respond.assert_called_once_with("Please provide a valid number between 1 and 11 to set the time")


def test_vibestatus_random_mode_summary(app, state_manager):
    register_status_command(app, state_manager)
    handler = app.get_command("/vibestatus")

    ack = Mock()
    respond = Mock()

    state = state_manager.get_state("T123")
    state.set_selected_mode("mode_random")
    state.set_active_channel("#general")
    state.set_daily_target_time("10:00:00 AM")
    state.set_random_start_time("09:30:00 AM")
    state.set_random_end_time("10:50:00 AM")

    handler(ack=ack, respond=respond, body={"team_id": "T123"})

    ack.assert_called_once()
    respond.assert_called_once()
    text = respond.call_args.args[0]
    assert "*Vibe Check Bot Status*" in text
    assert "*Mode:* Random (09:30:00 AM" in text
    assert "*Channel:* #general" in text


def test_vibestatus_static_mode_summary(app, state_manager):
    register_status_command(app, state_manager)
    handler = app.get_command("/vibestatus")

    ack = Mock()
    respond = Mock()

    state = state_manager.get_state("T123")
    state.set_selected_mode("mode_static")
    state.set_static_time("03:15:00 PM")
    state.set_active_channel("#general")

    handler(ack=ack, respond=respond, body={"team_id": "T123"})

    ack.assert_called_once()
    respond.assert_called_once()
    text = respond.call_args.args[0]
    assert "*Mode:* Static" in text
    assert "*Today's prompt time:* 03:15:00 PM" in text


def test_help_returns_setup_guide_text(app):
    register_help_command(app)
    handler = app.get_command("/help")

    ack = Mock()
    respond = Mock()

    handler(ack=ack, respond=respond)

    ack.assert_called_once()
    respond.assert_called_once()
    text = respond.call_args.args[0]
    assert "*Vibe Check Bot" in text
    assert "`/setchannel #your-channel-name`" in text


def test_streak_personal_no_streak(app):
    client = Mock()
    register_streak_command(app, client)
    handler = app.get_command("/streak")

    ack = Mock()
    respond = Mock()

    with patch("services.streak_service.get_user_streak", return_value=0):
        handler(ack=ack, command={"user_id": "U123", "user_name": "khai", "text": ""}, respond=respond)

    ack.assert_called_once()
    respond.assert_called_once_with("No streak yet, *khai*. Respond to today's prompt to get started.")


def test_streak_leaderboard_responds(app):
    client = Mock()
    client.users_info.return_value = {"user": {"profile": {"display_name": "Khai"}}}
    register_streak_command(app, client)
    handler = app.get_command("/streak")

    ack = Mock()
    respond = Mock()

    with patch("services.streak_service.get_all_streaks", return_value={"U123": 10}):
        handler(ack=ack, command={"user_id": "U123", "user_name": "khai", "text": "leaderboard"}, respond=respond)

    ack.assert_called_once()
    respond.assert_called_once()
    assert "*Streak Leaderboard*" in respond.call_args.args[0]
