# src/commands/user_prompt_command.py
import logging
import time

from bot.state import StateManager, get_team_id
from services.prompt_service import get_available_topics

_TIME_FORMAT = "%I:%M:%S %p"

_PRESET_TIME_OPTIONS = [
    {"text": {"type": "plain_text", "text": "09:30:00 AM"}, "value": "09:30:00 AM"},
    {"text": {"type": "plain_text", "text": "10:00:00 AM"}, "value": "10:00:00 AM"},
    {"text": {"type": "plain_text", "text": "10:30:00 AM"}, "value": "10:30:00 AM"},
    {"text": {"type": "plain_text", "text": "11:00:00 AM"}, "value": "11:00:00 AM"},
    {"text": {"type": "plain_text", "text": "11:30:00 AM"}, "value": "11:30:00 AM"},
    {"text": {"type": "plain_text", "text": "12:00:00 PM"}, "value": "12:00:00 PM"},
    {"text": {"type": "plain_text", "text": "12:30:00 PM"}, "value": "12:30:00 PM"},
    {"text": {"type": "plain_text", "text": "01:00:00 PM"}, "value": "01:00:00 PM"},
    {"text": {"type": "plain_text", "text": "02:00:00 PM"}, "value": "02:00:00 PM"},
    {"text": {"type": "plain_text", "text": "03:00:00 PM"}, "value": "03:00:00 PM"},
]


def send_user_prompt_invitation(client, user_id: str, team_id: str) -> None:
    """
    DM a user to invite them to create today's prompt.
    Called by the scheduler when it randomly selects a user.
    """
    try:
        client.chat_postMessage(
            channel=user_id,
            text="You've been selected to create today's vibe check prompt! :writing_hand:",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            ":writing_hand: *You've been selected to create today's vibe check prompt!*\n\n"
                            "You can write your own prompt, choose a topic, and pick when it goes out. "
                            "Hit the button below to get started."
                        ),
                    },
                },
                {
                    "type": "actions",
                    "block_id": f"user_prompt_invite|{team_id}",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": ":pencil: Create Today's Prompt"},
                            "action_id": "open_user_prompt_modal",
                            "style": "primary",
                        }
                    ],
                },
            ],
        )
        logging.info(f"[USER PROMPT] Sent prompt invitation to user {user_id} (team {team_id})")
    except Exception as e:
        logging.error(f"[USER PROMPT] Failed to DM user {user_id}: {e}")


def register_user_prompt_handlers(bolt_app, state_manager: StateManager):
    """
    Registers the action and modal handlers for the user-created daily prompt feature.
    """

    @bolt_app.action("open_user_prompt_modal")
    def handle_open_modal(ack, body, client):
        ack()

        team_id = get_team_id(body)
        expiry = int(time.time()) + 300  # 5-minute window from button click
        topics = get_available_topics()

        topic_options = [{"text": {"type": "plain_text", "text": t}, "value": t} for t in topics]

        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "user_prompt_modal",
                "private_metadata": f"{team_id}|{expiry}",
                "title": {"type": "plain_text", "text": "Create Today's Prompt"},
                "submit": {"type": "plain_text", "text": "Submit"},
                "close": {"type": "plain_text", "text": "Cancel"},
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Pick a topic for today's prompt — required. Then optionally write your own prompt below. If you leave it blank, a random prompt from that topic will be used.",
                        },
                    },
                    {
                        "type": "input",
                        "block_id": "topic_block",
                        "label": {"type": "plain_text", "text": "Topic"},
                        "element": {
                            "type": "static_select",
                            "action_id": "topic_select",
                            "placeholder": {"type": "plain_text", "text": "Pick a topic..."},
                            "options": topic_options,
                        },
                    },
                    {
                        "type": "input",
                        "block_id": "custom_prompt_block",
                        "optional": True,
                        "label": {"type": "plain_text", "text": "Write your own prompt (optional)"},
                        "hint": {"type": "plain_text", "text": "Leave blank to use a random prompt from the topic above."},
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "custom_prompt_input",
                            "multiline": True,
                            "placeholder": {"type": "plain_text", "text": "e.g. If you could live anywhere in the world, where would it be?"},
                        },
                    },
                    {
                        "type": "input",
                        "block_id": "time_block",
                        "optional": True,
                        "label": {"type": "plain_text", "text": "Send time"},
                        "hint": {"type": "plain_text", "text": "Leave blank to keep today's scheduled time."},
                        "element": {
                            "type": "static_select",
                            "action_id": "time_select",
                            "placeholder": {"type": "plain_text", "text": "Pick a time..."},
                            "options": _PRESET_TIME_OPTIONS,
                        },
                    },
                    {
                        "type": "input",
                        "block_id": "send_now_block",
                        "optional": True,
                        "label": {"type": "plain_text", "text": "Send immediately"},
                        "element": {
                            "type": "checkboxes",
                            "action_id": "send_now_check",
                            "options": [
                                {
                                    "text": {"type": "plain_text", "text": "Post the prompt to the channel right now"},
                                    "value": "send_now",
                                }
                            ],
                        },
                    },
                ],
            },
        )

    @bolt_app.view("user_prompt_modal")
    def handle_user_prompt_modal(ack, body, client):
        metadata = body["view"].get("private_metadata", "")
        parts = metadata.split("|", 1)
        team_id = parts[0] or get_team_id(body)
        expiry = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None

        if expiry and time.time() > expiry:
            ack(
                response_action="errors",
                errors={"topic_block": "Sorry, your 5-minute window to create a prompt has expired. The bot will use a regular prompt today."},
            )
            logging.info(f"[USER PROMPT] Submission rejected — window expired for team {team_id}")
            return

        ack()

        state = state_manager.get_state(team_id)
        values = body["view"]["state"]["values"]

        # Topic (required)
        topic_opt = (
            values.get("topic_block", {})
            .get("topic_select", {})
            .get("selected_option")
        )
        topic = topic_opt["value"] if topic_opt else None

        # Custom prompt text (optional)
        custom_text = (
            values.get("custom_prompt_block", {})
            .get("custom_prompt_input", {})
            .get("value") or ""
        ).strip()

        # Time (optional)
        time_opt = (
            values.get("time_block", {})
            .get("time_select", {})
            .get("selected_option")
        )
        selected_time = time_opt["value"] if time_opt else None

        # Send now checkbox (optional)
        send_now = bool(
            values.get("send_now_block", {})
            .get("send_now_check", {})
            .get("selected_options")
        )

        if send_now:
            from bot.posting import post_custom_prompt
            from services.prompt_service import get_random_prompt_by_topic
            channel = state.get_active_channel()
            prompt_text = custom_text or (get_random_prompt_by_topic(topic)[1] if topic else None)
            if prompt_text and channel:
                ts = post_custom_prompt(
                    client,
                    prompt_text,
                    channel=channel,
                    team_id=team_id,
                    prefix_text="Prompt of the day:",
                    footnote_text="user-created vibe check",
                )
                if ts:
                    state.set_last_prompt_ts(ts)
                logging.info(f"[USER PROMPT] Sent immediately to {channel} for team {team_id}")
        else:
            if custom_text:
                state.set_pending_custom_prompt(custom_text)
                logging.info(f"[USER PROMPT] Custom prompt set for team {team_id}: {custom_text!r}")
            elif topic:
                state.set_pending_topic(topic)
                logging.info(f"[USER PROMPT] Topic set for team {team_id}: {topic}")

            if selected_time:
                state.set_daily_target_time(selected_time)
                logging.info(f"[USER PROMPT] Time overridden for team {team_id}: {selected_time}")

        user_id = body["user"]["id"]
        summary_parts = []
        if send_now:
            summary_parts.append("sent to the channel now")
        else:
            if custom_text:
                summary_parts.append(f"prompt: _{custom_text}_")
            elif topic:
                summary_parts.append(f"topic: `{topic}`")
            else:
                summary_parts.append("a random prompt")
            if selected_time:
                summary_parts.append(f"at `{selected_time}`")

        client.chat_postMessage(
            channel=user_id,
            text=f":tada: Got it! Today's vibe check will use {' '.join(summary_parts)}. Thanks for contributing! :tada:",
        )
