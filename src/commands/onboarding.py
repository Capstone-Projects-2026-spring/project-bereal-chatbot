# src/commands/onboarding.py
import logging

from bot.state import StateManager, get_team_id
from services.prompt_service import get_available_topics
from services.mongo_service import save_user_interests, get_user_interests


def register_onboarding(bolt_app, state_manager: StateManager):
    """
    Sends new workspace members a DM with a topic interest checklist when they join.
    Tags are stored per-user and have no effect on which prompts are sent.
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

    @bolt_app.action("onboarding_choose_tags")
    def handle_onboarding_choose_tags(ack, body, client):
        ack()

        team_id = get_team_id(body)
        user_id = body["user"]["id"]

        topics = get_available_topics()
        if not topics:
            client.chat_postEphemeral(
                channel=user_id,
                user=user_id,
                text="No topics found yet, check back later!",
            )
            return

        existing_tags = set(get_user_interests(team_id, user_id))
        options = [
            {"text": {"type": "plain_text", "text": t}, "value": t}
            for t in topics
        ]
        initial_options = [opt for opt in options if opt["value"] in existing_tags]

        checkboxes_block = {
            "type": "input",
            "block_id": "interests_block",
            "optional": True,
            "label": {
                "type": "plain_text",
                "text": "Pick the topics that interest you",
            },
            "element": {
                "type": "checkboxes",
                "action_id": "selected_interests",
                "options": options,
            },
        }
        if initial_options:
            checkboxes_block["element"]["initial_options"] = initial_options

        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "user_interests_modal",
                "private_metadata": f"{team_id}|{user_id}",
                "title": {"type": "plain_text", "text": "Your Interests"},
                "submit": {"type": "plain_text", "text": "Save"},
                "close": {"type": "plain_text", "text": "Skip"},
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Select topics you're interested in, we'd love to get to know you better :smile:",
                        },
                    },
                    checkboxes_block,
                ],
            },
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
