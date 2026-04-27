# src/commands/control_panel_commands.py
from datetime import datetime
from services.time_library import preSet_time_library
from services.prompt_service import get_available_topics
from bot.state import get_team_id

_TIME_FORMAT = "%I:%M:%S %p"  # e.g. 09:15:00 AM


def _parse_time(value: str):
    """Return parsed datetime if value matches HH:MM:SS AM/PM, else None."""
    try:
        return datetime.strptime(value.strip().upper(), _TIME_FORMAT)
    except ValueError:
        return None

_PRESET_OPTIONS = [
    {"text": {"type": "plain_text", "text": "09:30:00 AM"}, "value": "time_1"},
    {"text": {"type": "plain_text", "text": "09:35:00 AM"}, "value": "time_2"},
    {"text": {"type": "plain_text", "text": "09:40:00 AM"}, "value": "time_3"},
    {"text": {"type": "plain_text", "text": "09:45:00 AM"}, "value": "time_4"},
    {"text": {"type": "plain_text", "text": "09:50:00 AM"}, "value": "time_5"},
    {"text": {"type": "plain_text", "text": "09:55:00 AM"}, "value": "time_6"},
    {"text": {"type": "plain_text", "text": "10:00:00 AM"}, "value": "time_7"},
    {"text": {"type": "plain_text", "text": "10:05:00 AM"}, "value": "time_8"},
    {"text": {"type": "plain_text", "text": "10:10:00 AM"}, "value": "time_9"},
    {"text": {"type": "plain_text", "text": "10:15:00 AM"}, "value": "time_10"},
    {"text": {"type": "plain_text", "text": "10:20:00 AM"}, "value": "time_11"},
    {"text": {"type": "plain_text", "text": "10:25:00 AM"}, "value": "time_12"},
    {"text": {"type": "plain_text", "text": "10:30:00 AM"}, "value": "time_13"},
    {"text": {"type": "plain_text", "text": "10:35:00 AM"}, "value": "time_14"},
    {"text": {"type": "plain_text", "text": "10:40:00 AM"}, "value": "time_15"},
    {"text": {"type": "plain_text", "text": "10:45:00 AM"}, "value": "time_16"},
    {"text": {"type": "plain_text", "text": "10:50:00 AM"}, "value": "time_17"},
]

_MODE_OPTIONS = [
    {"text": {"type": "plain_text", "text": "Random Time"}, "value": "mode_random"},
    {"text": {"type": "plain_text", "text": "Preset Time Select"}, "value": "mode_preset"},
    {"text": {"type": "plain_text", "text": "Static Set Time"}, "value": "mode_static"},
]

_PRESET_VALUE_MAP = {f"time_{i}": i for i in range(1, 18)}


_DAY_OPTIONS = [
    {"text": {"type": "plain_text", "text": d}, "value": d}
    for d in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
]

_RESPONSE_TYPE_OPTIONS = [
    {"text": {"type": "plain_text", "text": "Photo only (BeReal style)", "emoji": True}, "value": "image"},
    {"text": {"type": "plain_text", "text": "Text only", "emoji": True}, "value": "text"},
    {"text": {"type": "plain_text", "text": "Any (photo or text)", "emoji": True}, "value": "any"},
]


def _build_tag_options():
    topics = get_available_topics()
    return [{"text": {"type": "plain_text", "text": t}, "value": t} for t in topics]


def _build_topic_options():
    topics = get_available_topics()
    opts = [{"text": {"type": "plain_text", "text": "(any topic)"}, "value": "__none__"}]
    opts += [{"text": {"type": "plain_text", "text": t}, "value": t} for t in topics]
    return opts


def _build_home_view(selected_preset=None, selected_mode=None,
                     random_start=None, random_end=None, static_time=None,
                     active_days=None, pending_topic=None, active_tags=None,
                     reminder_enabled=False, prompt_response_type="image") -> dict:
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

    if active_days is None:
        active_days = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}
    day_initial = [opt for opt in _DAY_OPTIONS if opt["value"] in active_days]

    tag_options = _build_tag_options()
    tag_initial = [opt for opt in tag_options if opt["value"] in (active_tags or set())]

    topic_options = _build_topic_options()
    topic_initial = next(
        (opt for opt in topic_options if opt["value"] == (pending_topic or "__none__")),
        topic_options[0]
    )

    # --- always-visible blocks ---
    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "Vibe Check Bot Settings"}
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*1. Select Operation Mode*"},
            "accessory": mode_accessory
        },
        {"type": "divider"},
    ]

    # --- dynamic time config based on selected mode ---
    if selected_mode == "mode_random":
        start_element = {
            "type": "plain_text_input",
            "action_id": "start_time",
            "placeholder": {"type": "plain_text", "text": "HH:MM:SS AM/PM  e.g. 09:00:00 AM"}
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

        blocks += [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Random Time Range\nSet a window — the bot picks a random time within it each day."}
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
        ]

    elif selected_mode == "mode_preset":
        preset_initial = next(
            (opt for opt in _PRESET_OPTIONS if opt["value"] == selected_preset),
            _PRESET_OPTIONS[0]
        )
        blocks += [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Preset Time\nPick one of the preset times."}
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "static_select",
                        "placeholder": {"type": "plain_text", "text": "Select a time..."},
                        "initial_option": preset_initial,
                        "options": _PRESET_OPTIONS,
                        "action_id": "preset_time_selection"
                    }
                ]
            },
            {"type": "divider"},
        ]

    elif selected_mode == "mode_static":
        static_element = {
            "type": "plain_text_input",
            "action_id": "static_entry",
            "placeholder": {"type": "plain_text", "text": "HH:MM:SS AM/PM  e.g. 09:15:00 AM"}
        }
        if static_time:
            static_element["initial_value"] = static_time

        blocks += [
            {
                "type": "input",
                "dispatch_action": True,
                "element": static_element,
                "label": {"type": "plain_text", "text": "Static Set Time"}
            },
            {"type": "divider"},
        ]

    else:
        # No mode selected yet — prompt the user
        blocks += [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "_Select a mode above to configure its time settings._"}
            },
            {"type": "divider"},
        ]

    # --- always-visible: active days ---
    blocks += [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*2. Active Days*"}
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "checkboxes",
                    "action_id": "active_days_selection",
                    "initial_options": day_initial,
                    "options": _DAY_OPTIONS
                }
            ]
        },
        {"type": "divider"},
    ]

    # --- always-visible: tag filter ---
    tag_filter_block = {
        "type": "actions",
        "elements": [
            {
                "type": "checkboxes",
                "action_id": "tag_filter_selection",
                "options": tag_options,
            }
        ]
    }
    if tag_initial:
        tag_filter_block["elements"][0]["initial_options"] = tag_initial

    blocks += [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*3. Topic Filter*\nOnly send prompts from these tags. Leave all unchecked for any topic."}
        },
        tag_filter_block,
        {"type": "divider"},
    ]

    # --- always-visible: next prompt one-time override ---
    blocks += [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*4. Next Prompt Override*\nForce the next scheduled prompt to use a specific topic. Resets after it fires."}
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "static_select",
                    "placeholder": {"type": "plain_text", "text": "Pick a topic..."},
                    "initial_option": topic_initial,
                    "options": topic_options,
                    "action_id": "topic_selection"
                }
            ]
        },
        {"type": "divider"},
    ]

    reminder_block = {
        "type": "actions",
        "elements": [
            {
                "type": "checkboxes",
                "action_id": "reminder_toggle",
                "options": [
                    {
                        "text": {"type": "plain_text", "text": "Send DM reminders 30 min after a prompt posts"},
                        "value": "reminder_enabled"
                    }
                ]
            }
        ]
    }
    if reminder_enabled:
        reminder_block["elements"][0]["initial_options"] = [
            {
                "text": {"type": "plain_text", "text": "Send DM reminders 30 min after a prompt posts"},
                "value": "reminder_enabled"
            }
        ]

    response_type_initial = next(
        (opt for opt in _RESPONSE_TYPE_OPTIONS if opt["value"] == prompt_response_type),
        _RESPONSE_TYPE_OPTIONS[0]
    )

    blocks += [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*5. Late Response Reminders*\nDM users who haven't responded 30 minutes after a vibe check posts."}
        },
        reminder_block,
        {"type": "divider"},
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*6. Prompt Type*\nChoose whether prompts ask for a photo, a text response, or either."}
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "radio_buttons",
                    "action_id": "response_type_selection",
                    "initial_option": response_type_initial,
                    "options": _RESPONSE_TYPE_OPTIONS,
                }
            ]
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*7. Assign Prompt Creator*\nPick a user to DM them the prompt creation invite! They will have 5 minutes to submit."}
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "users_select",
                    "placeholder": {"type": "plain_text", "text": "Select a user..."},
                    "action_id": "admin_assign_prompt_creator"
                }
            ]
        },
    ]

    return {"type": "home", "blocks": blocks}


def _publish_home(client, user_id, state):
    client.views_publish(
        user_id=user_id,
        view=_build_home_view(
            selected_preset=state.get_selected_preset(),
            selected_mode=state.get_selected_mode(),
            random_start=state.get_random_start_time(),
            random_end=state.get_random_end_time(),
            static_time=state.get_static_time(),
            active_days=state.get_active_days(),
            pending_topic=state._pending_topic,
            active_tags=state.get_active_tags(),
            reminder_enabled=state.get_reminder_enabled(),
            prompt_response_type=state.get_prompt_response_type(),
        )
    )


def _dm_admin(client, user_id, message):
    client.chat_postMessage(channel=user_id, text=message)


def _repick_random_time(client, user_id, state):
    """Re-pick today's target time from the current range and announce it. Only acts in random mode."""
    from datetime import datetime
    from bot.scheduler import _pick_random_time
    mode = state.get_selected_mode()
    if mode not in ("mode_random", None):
        return
    new_time = _pick_random_time(
        state.get_random_start_time(),
        state.get_random_end_time(),
        after=datetime.now()
    )
    state.set_daily_target_time(new_time)
    print(f"[CONTROL PANEL] Re-picked daily target time: {new_time}")
    _dm_admin(client, user_id, f":dart: New target time for today: `{new_time}`")


def register_control_panel(bolt_app, state_manager):
    @bolt_app.event("app_home_opened")
    def update_home_tab(client, event, body, logger):
        try:
            team_id = get_team_id(body)
            state = state_manager.get_state(team_id)
            _publish_home(client, event["user"], state)
        except Exception as e:
            logger.error(f"Error publishing home tab: {e}")

    @bolt_app.action("mode_selection")
    def handle_mode_selection(ack, body, client, logger):
        ack()
        team_id = get_team_id(body)
        state = state_manager.get_state(team_id)
        value = body["actions"][0]["selected_option"]["value"]
        state.set_selected_mode(value)
        state.set_active_token(client.token)
        print(f"[CONTROL PANEL] [{team_id}] Operation mode set to: {value}")
        logger.info(f"Mode selected: {value}")
        _publish_home(client, body["user"]["id"], state)
        _dm_admin(client, body["user"]["id"], f":gear: *Operation mode* changed to `{value}`")
        _repick_random_time(client, body["user"]["id"], state)

    @bolt_app.action("start_time")
    def handle_start_time(ack, body, client, logger):
        ack()
        team_id = get_team_id(body)
        state = state_manager.get_state(team_id)
        value = body["actions"][0]["value"]
        parsed = _parse_time(value)
        if not parsed:
            _dm_admin(client, body["user"]["id"],
                      f":x: *Invalid start time* `{value}` — must be `HH:MM:SS AM/PM` (e.g. `12:00:00 PM`)")
            return
        normalized = parsed.strftime("%I:%M:%S %p")
        state.set_random_start_time(normalized)
        print(f"[CONTROL PANEL] [{team_id}] Random start time set to: {normalized}")
        logger.info(f"Random start time set: {normalized}")
        _dm_admin(client, body["user"]["id"], f":clock1: *Random range start* set to `{normalized}`")
        _repick_random_time(client, body["user"]["id"], state)

    @bolt_app.action("end_time")
    def handle_end_time(ack, body, client, logger):
        ack()
        team_id = get_team_id(body)
        state = state_manager.get_state(team_id)
        value = body["actions"][0]["value"]
        parsed = _parse_time(value)
        if not parsed:
            _dm_admin(client, body["user"]["id"],
                      f":x: *Invalid end time* `{value}` — must be `HH:MM:SS AM/PM` (e.g. `05:00:00 PM`)")
            return
        normalized = parsed.strftime("%I:%M:%S %p")
        state.set_random_end_time(normalized)
        print(f"[CONTROL PANEL] [{team_id}] Random end time set to: {normalized}")
        logger.info(f"Random end time set: {normalized}")
        _dm_admin(client, body["user"]["id"], f":clock1: *Random range end* set to `{normalized}`")
        _repick_random_time(client, body["user"]["id"], state)

    @bolt_app.action("static_entry")
    def handle_static_entry(ack, body, client, logger):
        ack()
        team_id = get_team_id(body)
        state = state_manager.get_state(team_id)
        value = body["actions"][0]["value"]
        parsed = _parse_time(value)
        if not parsed:
            _dm_admin(client, body["user"]["id"],
                      f":x: *Invalid static time* `{value}` — must be `HH:MM:SS AM/PM` (e.g. `09:15:00 AM`)")
            return
        normalized = parsed.strftime("%I:%M:%S %p")
        state.set_static_time(normalized)
        print(f"[CONTROL PANEL] [{team_id}] Static time set to: {normalized}")
        logger.info(f"Static time set: {normalized}")
        _dm_admin(client, body["user"]["id"], f":clock1: *Static time* set to `{normalized}`")

    @bolt_app.action("active_days_selection")
    def handle_active_days(ack, body, client, logger):
        ack()
        team_id = get_team_id(body)
        state = state_manager.get_state(team_id)
        selected = body["actions"][0].get("selected_options", [])
        days = {opt["value"] for opt in selected}
        state.set_active_days(days)
        day_list = ", ".join(sorted(days)) if days else "none"
        print(f"[CONTROL PANEL] [{team_id}] Active days set to: {day_list}")
        logger.info(f"Active days set: {day_list}")
        _publish_home(client, body["user"]["id"], state)
        _dm_admin(client, body["user"]["id"], f":calendar: *Active days* set to: {day_list}")

    @bolt_app.action("preset_time_selection")
    def handle_preset_time_selection(ack, body, client, logger):
        ack()
        team_id = get_team_id(body)
        state = state_manager.get_state(team_id)
        value = body["actions"][0]["selected_option"]["value"]
        index = _PRESET_VALUE_MAP.get(value)
        if index is not None:
            t = preSet_time_library(index)
            state.set_daily_target_time(t)
            state.set_selected_preset(value)
            print(f"[CONTROL PANEL] [{team_id}] Preset time selected: {t}")
            logger.info(f"Preset time selected: {t}")
            _publish_home(client, body["user"]["id"], state)
            _dm_admin(client, body["user"]["id"], f":clock1: *Preset time* set to `{t}`")

    @bolt_app.action("topic_selection")
    def handle_topic_selection(ack, body, client, logger):
        ack()
        team_id = get_team_id(body)
        state = state_manager.get_state(team_id)
        value = body["actions"][0]["selected_option"]["value"]
        if value == "__none__":
            state.set_pending_topic(None)
            print(f"[CONTROL PANEL] [{team_id}] Topic cleared (any)")
            _dm_admin(client, body["user"]["id"], "No topic selected — topic will still be random.")
        else:
            state.set_pending_topic(value)
            print(f"[CONTROL PANEL] [{team_id}] Pending topic set to: {value}")
            logger.info(f"Pending topic set: {value}")
            _dm_admin(client, body["user"]["id"], f"Next prompt topic set to `{value}`.")
        _publish_home(client, body["user"]["id"], state)

    @bolt_app.action("tag_filter_selection")
    def handle_tag_filter_selection(ack, body, client, logger):
        ack()
        team_id = get_team_id(body)
        state = state_manager.get_state(team_id)
        selected = body["actions"][0].get("selected_options", [])
        tags = {opt["value"] for opt in selected}
        state.set_active_tags(tags)
        tag_list = ", ".join(sorted(tags)) if tags else "any"
        print(f"[CONTROL PANEL] [{team_id}] Active tag filter set to: {tag_list}")
        logger.info(f"Tag filter set: {tag_list}")
        _publish_home(client, body["user"]["id"], state)
        _dm_admin(client, body["user"]["id"], f":label: *Topic filter* set to: {tag_list}")

    @bolt_app.action("reminder_toggle")
    def handle_reminder_toggle(ack, body, client, logger):
        ack()
        team_id = get_team_id(body)
        state = state_manager.get_state(team_id)
        selected = body["actions"][0].get("selected_options", [])
        enabled = any(opt["value"] == "reminder_enabled" for opt in selected)
        state.set_reminder_enabled(enabled)
        status = "enabled" if enabled else "disabled"
        print(f"[CONTROL PANEL] [{team_id}] Late response reminders {status}")
        logger.info(f"Reminder toggle: {status}")
        _publish_home(client, body["user"]["id"], state)
        _dm_admin(client, body["user"]["id"], f":bell: *Late response reminders* {status}")

    @bolt_app.action("response_type_selection")
    def handle_response_type_selection(ack, body, client, logger):
        ack()
        team_id = get_team_id(body)
        state = state_manager.get_state(team_id)
        value = body["actions"][0]["selected_option"]["value"]
        state.set_prompt_response_type(value)
        labels = {"image": "Photo only", "text": "Text only", "any": "Any (photo or text)"}
        label = labels.get(value, value)
        print(f"[CONTROL PANEL] [{team_id}] Prompt response type set to: {value}")
        logger.info(f"Prompt response type set: {value}")
        _publish_home(client, body["user"]["id"], state)
        _dm_admin(client, body["user"]["id"], f":camera: *Prompt type* set to: *{label}*")

    @bolt_app.action("admin_assign_prompt_creator")
    def handle_admin_assign_prompt_creator(ack, body, client, logger):
        ack()
        team_id = get_team_id(body)
        selected_user = body["actions"][0].get("selected_user")
        if not selected_user:
            return
        from commands.user_prompt_command import send_user_prompt_invitation
        send_user_prompt_invitation(client, selected_user, team_id)
        print(f"[CONTROL PANEL] [{team_id}] Admin assigned prompt creator: {selected_user}")
        logger.info(f"Admin assigned prompt creator: {selected_user}")
        _dm_admin(client, body["user"]["id"], f":pencil: Prompt creation invite sent to <@{selected_user}>.")
