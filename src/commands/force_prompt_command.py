# src/commands/force_prompt_command.py
import logging

from services.prompt_service import get_random_prompt_text, mark_prompt_asked
from services.mongo_service import get_tracker


def _post_random_prompt(client, channel="#bot-test", response_type=None, prefix_text=None):
    """
    Pull a random prompt from the prompt service and post it to Slack.
    """
    prompt_id, prompt_text, tags = get_random_prompt_text(response_type=response_type)
    mark_prompt_asked(prompt_id)

    tracker = get_tracker()
    if tracker:
        tracker.record_prompt_sent(prompt_id, prompt_text, tags, channel)

    message = prompt_text
    if prefix_text:
        message = f"{prefix_text}\n\n{prompt_text}"

    msg_block = [{
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": "Testing the sending of a block.",
                    }
                }
            ]
        }]
    
    msg_block2 = [
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": "Testing the sending of a block." + message,
                    }
                }
        ]
    
    
    client.chat_postMessage(channel=channel, blocks=msg_block2, text=message)

   # client.chat_postMessage(channel=channel, text=message)
    logging.info(f"Force prompt posted prompt_id={prompt_id} to {channel}")


def register_force_prompt_command(bolt_app):
    """
    Registers a slash command:
      /forceprompt
      /forceprompt text
      /forceprompt image
      /forceprompt #some-channel
      /forceprompt text #some-channel
    """

    @bolt_app.command("/forceprompt")
    def force_prompt(ack, respond, body, client):
        ack()

        text = (body.get("text") or "").strip()
        parts = text.split()

        response_type = None
        channel = body.get("channel_id")  # default to the channel where command was used

        # Parse args in any order:
        # - "text" or "image"
        # - "#channel"
        for p in parts:
            pl = p.lower()
            if pl in ("text", "image"):
                response_type = pl
            elif p.startswith("#"):
                channel = p

        try:
            _post_random_prompt(
                client=client,
                channel=channel,
                response_type=response_type,
                prefix_text="Forced vibe check prompt:"
            )
            respond(f"✅ Posted a prompt to {channel}.")
        except Exception as e:
            logging.exception("Error in /forceprompt")
            respond(f"❌ Failed to post prompt: {e}")