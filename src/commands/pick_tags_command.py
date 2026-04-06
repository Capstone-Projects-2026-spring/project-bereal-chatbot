# src/commands/pick_tags_command.py
import logging

from bot.state import StateManager, get_team_id
from services.prompt_service import get_available_topics


def register_pick_tags_command(bolt_app, state_manager: StateManager):
    """
    Registers /picktags — opens a modal so users can select which topic tags
    prompts should be drawn from. Selecting none means all topics are allowed.
    """

    @bolt_app.command("/picktags")
    def pick_tags(ack, body, client):
        ack()

        team_id = get_team_id(body)
        state = state_manager.get_state(team_id)
        active_tags = state.get_active_tags()

        topics = get_available_topics()
        if not topics:
            client.chat_postEphemeral(
                channel=body["channel_id"],
                user=body["user_id"],
                text="No topics found in the prompt CSV.",
            )
            return

        options = [
            {"text": {"type": "plain_text", "text": t}, "value": t}
            for t in topics
        ]
        initial_options = [opt for opt in options if opt["value"] in active_tags]

        checkboxes_block = {
            "type": "input",
            "block_id": "tag_selection_block",
            "optional": True,
            "label": {
                "type": "plain_text",
                "text": "Select topics (leave all unchecked for any topic)",
            },
            "element": {
                "type": "checkboxes",
                "action_id": "selected_tags",
                "options": options,
            },
        }
        if initial_options:
            checkboxes_block["element"]["initial_options"] = initial_options

        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "pick_tags_modal",
                "private_metadata": team_id or "",
                "title": {"type": "plain_text", "text": "Pick Prompt Topics"},
                "submit": {"type": "plain_text", "text": "Save"},
                "close": {"type": "plain_text", "text": "Cancel"},
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Choose which topic tags to include in scheduled prompts. Leave all unchecked to allow *any* topic.",
                        },
                    },
                    checkboxes_block,
                ],
            },
        )

    @bolt_app.view("pick_tags_modal")
    def handle_pick_tags_modal(ack, body, client):
        ack()

        team_id = body["view"].get("private_metadata") or get_team_id(body)
        state = state_manager.get_state(team_id)

        selected = (
            body["view"]["state"]["values"]
            .get("tag_selection_block", {})
            .get("selected_tags", {})
            .get("selected_options", [])
        )
        tags = {opt["value"] for opt in selected}
        state.set_active_tags(tags)

        tag_list = ", ".join(f"`{t}`" for t in sorted(tags)) if tags else "any topic"
        user_id = body["user"]["id"]
        logging.info(f"/picktags set active_tags={tags} for team={team_id}")

        client.chat_postEphemeral(
            channel=user_id,
            user=user_id,
            text=f":label: Topic filter updated — prompts will now be drawn from: {tag_list}.",
        )
