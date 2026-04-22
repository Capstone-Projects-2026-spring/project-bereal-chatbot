# src/commands/onboarding.py
import logging

from bot.state import StateManager, get_team_id
from services.mongo_service import get_user_interests, save_user_interests


_INTEREST_OPTIONS = [
    {"text": {"type": "plain_text", "text": "Sports"}, "value": "sports"},
    {"text": {"type": "plain_text", "text": "Food"}, "value": "food"},
    {"text": {"type": "plain_text", "text": "Hobbies"}, "value": "hobbies"},
    {"text": {"type": "plain_text", "text": "Personal Life"}, "value": "personal_life"},
    {"text": {"type": "plain_text", "text": "TV and Movies"}, "value": "tv_movies"},
    {"text": {"type": "plain_text", "text": "Work Life"}, "value": "work_life"},
    {"text": {"type": "plain_text", "text": "Would You Rather"}, "value": "would_you_rather"},
]


def _extract_user_id(body) -> str | None:
    if body.get("user", {}).get("id"):
        return body["user"]["id"]
    return body.get("user_id")


def _build_interests_modal(team_id: str, user_id: str, current_tags: list[str]) -> dict:
    valid_values = {option["value"] for option in _INTEREST_OPTIONS}
    selected_values = [tag for tag in current_tags if tag in valid_values]
    initial_options = [option for option in _INTEREST_OPTIONS if option["value"] in selected_values]

    checkboxes_element = {
        "type": "checkboxes",
        "action_id": "selected_interests",
        "options": _INTEREST_OPTIONS,
    }
    if initial_options:
        checkboxes_element["initial_options"] = initial_options

    return {
        "type": "modal",
        "callback_id": "user_interests_modal",
        "private_metadata": f"{team_id}|{user_id}",
        "title": {"type": "plain_text", "text": "Your Interests"},
        "submit": {"type": "plain_text", "text": "Save"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Select the topics you like so we can get a general sense of your interests.",
                },
            },
            {
                "type": "input",
                "block_id": "interests_block",
                "optional": True,
                "label": {
                    "type": "plain_text",
                    "text": "Pick the topics that interest you",
                },
                "element": checkboxes_element,
            },
        ],
    }


def register_onboarding(bolt_app, state_manager: StateManager):
    """
    Sends new workspace members a DM with a topic interest checklist when they join.
    Tags are stored per-user to help the bot make soft social introductions.
    """

    @bolt_app.event("team_join")
    def handle_team_join(event, client, body):
        user = event.get("user", {})
        user_id = user.get("id") if isinstance(user, dict) else user
        if not user_id:
            return

        try:
            client.chat_postMessage(
                channel=user_id,
                text="Welcome to Vibe Check! :wave: Choose which prompt topics interest you.",
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": (
                                ":wave: *Welcome to Vibe Check!*\n\n"
                                "The bot sends regular prompts to get the team sharing and connecting. "
                                "Let us know which *topics* interest you!"
                                "Hit the button below to pick your interests."
                            ),
                        },
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {"type": "plain_text", "text": ":label: Choose Interests"},
                                "action_id": "onboarding_choose_tags",
                                "style": "primary",
                            }
                        ],
                    },
                ],
            )
            logging.info(f"[ONBOARDING] Sent welcome DM to user {user_id}")
        except Exception as e:
            logging.error(f"[ONBOARDING] Failed to DM user {user_id}: {e}")

    @bolt_app.command("/picktags")
    def handle_picktags_command(ack, body, client):
        ack()
        _open_interests_modal(body, client)

    @bolt_app.action("onboarding_choose_tags")
    def handle_onboarding_choose_tags(ack, body, client):
        ack()
        _open_interests_modal(body, client)

    def _open_interests_modal(body, client):
        team_id = get_team_id(body)
        user_id = _extract_user_id(body)
        trigger_id = body.get("trigger_id")
        if not user_id or not trigger_id:
            logging.warning("[ONBOARDING] Could not open interests modal, missing user_id or trigger_id")
            return

        current_tags = get_user_interests(team_id, user_id)

        client.views_open(
            trigger_id=trigger_id,
            view=_build_interests_modal(team_id, user_id, current_tags),
        )

    @bolt_app.view("user_interests_modal")
    def handle_user_interests_modal(ack, body, client):
        ack()

        metadata = body["view"].get("private_metadata", "|")
        parts = metadata.split("|", 1)
        team_id = parts[0] if parts[0] else get_team_id(body)
        user_id = parts[1] if len(parts) > 1 and parts[1] else body["user"]["id"]

        selected = (
            body["view"]["state"]["values"]
            .get("interests_block", {})
            .get("selected_interests", {})
            .get("selected_options", [])
        )
        tags = [opt["value"] for opt in selected]
        save_user_interests(team_id, user_id, tags)

        tag_list = ", ".join(f"`{t}`" for t in sorted(tags)) if tags else "nothing yet"
        logging.info(f"[ONBOARDING] Saved interests for user {user_id}: {tags}")

        client.chat_postMessage(
            channel=user_id,
            text=f":white_check_mark: Got it! Your interests are saved as: {tag_list}. You can update them anytime with `/picktags`.",
        )
