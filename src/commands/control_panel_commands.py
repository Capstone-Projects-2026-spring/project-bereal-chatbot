# src/commands/control_panel_commands.py
from datetime import datetime
from services.time_library import preSet_time_library

_TIME_FORMAT = "%I:%M:%S %p"  # e.g. 09:15:00 AM


def _parse_time(value: str):
    """Return parsed datetime if value matches HH:MM:SS AM/PM, else None."""
    try:
        return datetime.strptime(value.strip().upper(), _TIME_FORMAT)
    except ValueError:
        return None

_PRESET_OPTIONS = [
    {"text": {"type": "plain_text", "text": "12:00:00 PM"}, "value": "time_1"},
    {"text": {"type": "plain_text", "text": "12:30:00 PM"}, "value": "time_2"},
    {"text": {"type": "plain_text", "text": "01:00:00 PM"}, "value": "time_3"},
    {"text": {"type": "plain_text", "text": "01:30:00 PM"}, "value": "time_4"},
    {"text": {"type": "plain_text", "text": "02:00:00 PM"}, "value": "time_5"},
    {"text": {"type": "plain_text", "text": "02:30:00 PM"}, "value": "time_6"},
    {"text": {"type": "plain_text", "text": "03:00:00 PM"}, "value": "time_7"},
    {"text": {"type": "plain_text", "text": "03:30:00 PM"}, "value": "time_8"},
    {"text": {"type": "plain_text", "text": "04:00:00 PM"}, "value": "time_9"},
    {"text": {"type": "plain_text", "text": "04:30:00 PM"}, "value": "time_10"},
]

_MODE_OPTIONS = [
    {"text": {"type": "plain_text", "text": "Random Time"}, "value": "mode_random"},
    {"text": {"type": "plain_text", "text": "Preset Time Select"}, "value": "mode_preset"},
    {"text": {"type": "plain_text", "text": "Static Set Time"}, "value": "mode_static"},
]

_PRESET_VALUE_MAP = {f"time_{i}": i for i in range(1, 11)}


def _build_home_view(selected_preset=None, selected_mode=None,
                     random_start=None, random_end=None, static_time=None) -> dict:
    preset_initial = next(
        (opt for opt in _PRESET_OPTIONS if opt["value"] == selected_preset),
        _PRESET_OPTIONS[0]
    )
    mode_initial = next(
        (opt for opt in _MODE_OPTIONS if opt["value"] == selected_mode),
        None
    )

    mode_accessory = {
        "type": "radio_buttons",
        "options": _MODE_OPTIONS,
        "action_id": "mode_selection"
    }
    if mode_initial:
        mode_accessory["initial_option"] = mode_initial

    start_element = {
        "type": "plain_text_input",
        "action_id": "start_time",
        "placeholder": {"type": "plain_text", "text": "HH:MM:SS AM/PM  e.g. 12:00:00 PM"}
    }
    if random_start:
        start_element["initial_value"] = random_start

    end_element = {
        "type": "plain_text_input",
        "action_id": "end_time",
        "placeholder": {"type": "plain_text", "text": "HH:MM:SS AM/PM  e.g. 05:00:00 PM"}
    }
    if random_end:
        end_element["initial_value"] = random_end

    static_element = {
        "type": "plain_text_input",
        "action_id": "static_entry",
        "placeholder": {"type": "plain_text", "text": "HH:MM:SS AM/PM  e.g. 09:15:00 AM"}
    }
    if static_time:
        static_element["initial_value"] = static_time

    return {
        "type": "home",
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "Time Configuration Settings"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*1. Select Operation Mode*"},
                "accessory": mode_accessory
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*2. Random Time Range Parameters:*"}
            },
            {
                "type": "input",
                "dispatch_action": True,
                "element": start_element,
                "label": {"type": "plain_text", "text": "Start Time"}
            },
            {
                "type": "input",
                "dispatch_action": True,
                "element": end_element,
                "label": {"type": "plain_text", "text": "End Time"}
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*3. Preset Times Select:*"}
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "radio_buttons",
                        "initial_option": preset_initial,
                        "options": _PRESET_OPTIONS,
                        "action_id": "preset_time_selection"
                    }
                ]
            },
            {"type": "divider"},
            {
                "type": "input",
                "dispatch_action": True,
                "element": static_element,
                "label": {"type": "plain_text", "text": "*4. Static Set Time (Manual)*"}
            }
        ]
    }


def _publish_home(client, user_id, state):
    client.views_publish(
        user_id=user_id,
        view=_build_home_view(
            selected_preset=state.get_selected_preset(),
            selected_mode=state.get_selected_mode(),
            random_start=state.get_random_start_time(),
            random_end=state.get_random_end_time(),
            static_time=state.get_static_time(),
        )
    )


def _dm_admin(client, user_id, message):
    client.chat_postMessage(channel=user_id, text=message)


def register_control_panel(bolt_app, state):
    @bolt_app.event("app_home_opened")
    def update_home_tab(client, event, logger):
        try:
            _publish_home(client, event["user"], state)
        except Exception as e:
            logger.error(f"Error publishing home tab: {e}")

    @bolt_app.action("mode_selection")
    def handle_mode_selection(ack, body, client, logger):
        ack()
        value = body["actions"][0]["selected_option"]["value"]
        state.set_selected_mode(value)
        print(f"[CONTROL PANEL] Operation mode set to: {value}")
        logger.info(f"Mode selected: {value}")
        _publish_home(client, body["user"]["id"], state)
        _dm_admin(client, body["user"]["id"], f":gear: *Operation mode* changed to `{value}`")

    @bolt_app.action("start_time")
    def handle_start_time(ack, body, client, logger):
        ack()
        value = body["actions"][0]["value"]
        if not _parse_time(value):
            _dm_admin(client, body["user"]["id"],
                      f":x: *Invalid start time* `{value}` — must be `HH:MM:SS AM/PM` (e.g. `12:00:00 PM`)")
            return
        state.set_random_start_time(value.strip())
        print(f"[CONTROL PANEL] Random start time set to: {value}")
        logger.info(f"Random start time set: {value}")
        _dm_admin(client, body["user"]["id"], f":clock1: *Random range start* set to `{value.strip()}`")

    @bolt_app.action("end_time")
    def handle_end_time(ack, body, client, logger):
        ack()
        value = body["actions"][0]["value"]
        if not _parse_time(value):
            _dm_admin(client, body["user"]["id"],
                      f":x: *Invalid end time* `{value}` — must be `HH:MM:SS AM/PM` (e.g. `05:00:00 PM`)")
            return
        state.set_random_end_time(value.strip())
        print(f"[CONTROL PANEL] Random end time set to: {value}")
        logger.info(f"Random end time set: {value}")
        _dm_admin(client, body["user"]["id"], f":clock1: *Random range end* set to `{value.strip()}`")

    @bolt_app.action("static_entry")
    def handle_static_entry(ack, body, client, logger):
        ack()
        value = body["actions"][0]["value"]
        if not _parse_time(value):
            _dm_admin(client, body["user"]["id"],
                      f":x: *Invalid static time* `{value}` — must be `HH:MM:SS AM/PM` (e.g. `09:15:00 AM`)")
            return
        state.set_static_time(value.strip())
        print(f"[CONTROL PANEL] Static time set to: {value}")
        logger.info(f"Static time set: {value}")
        _dm_admin(client, body["user"]["id"], f":clock1: *Static time* set to `{value.strip()}`")

    @bolt_app.action("preset_time_selection")
    def handle_preset_time_selection(ack, body, client, logger):
        ack()
        value = body["actions"][0]["selected_option"]["value"]
        index = _PRESET_VALUE_MAP.get(value)
        if index is not None:
            t = preSet_time_library(index)
            state.set_daily_target_time(t)
            state.set_selected_preset(value)
            print(f"[CONTROL PANEL] Preset time selected: {t}")
            logger.info(f"Preset time selected: {t}")
            _publish_home(client, body["user"]["id"], state)
            _dm_admin(client, body["user"]["id"], f":clock1: *Preset time* set to `{t}`")
