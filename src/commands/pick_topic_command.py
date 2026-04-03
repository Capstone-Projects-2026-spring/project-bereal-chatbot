# src/commands/pick_topic_command.py
import logging

from bot.state import StateManager, get_team_id
from services.prompt_service import get_available_topics


def register_pick_topic_command(bolt_app, state_manager: StateManager):
    """
    Registers the /picktopic slash command.

    Usage:
      /picktopic             — list all available topics
      /picktopic food        — set the next prompt's topic to "food"
    """

    @bolt_app.command("/picktopic")
    def pick_topic(ack, respond, body):
        ack()

        text = (body.get("text") or "").strip()

        # No args — show available topics
        if not text:
            topics = get_available_topics()
            if topics:
                topic_list = "\n".join(f"  • `{t}`" for t in topics)
                respond(
                    f"*Available topics:*\n{topic_list}\n\n"
                    f"Usage: `/picktopic <topic>` — the next scheduled prompt will use that topic."
                )
            else:
                respond("No topics found in the prompt CSV.")
            return

        topic = text.split()[0]  # take first word as topic

        # Validate the topic exists
        available = get_available_topics()
        if available and topic.lower() not in [t.lower() for t in available]:
            topic_list = ", ".join(f"`{t}`" for t in available)
            respond(f"Unknown topic `{topic}`. Pick from the available topics: {topic_list}")
            return

        team_id = get_team_id(body)
        if team_id:
            state = state_manager.get_state(team_id)
            state.set_pending_topic(topic.lower())

        respond(f"Topic set, the next prompt will be from the `{topic}` topic.")
        logging.info(f"/picktopic set pending topic={topic} for team={team_id}")


