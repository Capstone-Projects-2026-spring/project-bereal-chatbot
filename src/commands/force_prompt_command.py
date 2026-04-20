# src/commands/force_prompt_command.py
import logging
import random

from services.prompt_service import get_random_prompt_text, mark_prompt_asked
from services.mongo_service import get_tracker


def _post_random_prompt(client, channel="#bot-test", team_id="", response_type=None, prefix_text=None, footnote_text=None, active_tags=None):
    """
    Pull a random prompt from the prompt service and post it to Slack.
    Returns the message timestamp (ts) so callers can track it for reminders.
    """
    prompt_id, prompt_text, tags = get_random_prompt_text(response_type=response_type, active_tags=active_tags)
    mark_prompt_asked(prompt_id)

    tracker = get_tracker()
    if tracker:
        tracker.record_prompt_sent(prompt_id, prompt_text, tags, channel, team_id)

    message = f">{prompt_text}"
    if prefix_text:
        message = f"### **{prefix_text.upper()}**\n\n>{prompt_text}"

    if footnote_text:
        message += f"\n\n\n```{footnote_text}```"

    msg_block = randomize_message_block(message)

    resp = client.chat_postMessage(channel=channel, blocks=msg_block, text=message)
    logging.info(f"Force prompt posted prompt_id={prompt_id} to {channel}")
    return resp.get("ts")


def register_force_prompt_command(bolt_app, state_manager=None):
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
        team_id = body.get("team_id") or (body.get("authorizations") or [{}])[0].get("team_id") or ""

        active_tags = None
        if state_manager and team_id:
            active_tags = state_manager.get_state(team_id).get_active_tags() or None

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
            ts = _post_random_prompt(
                client=client,
                channel=channel,
                team_id=team_id,
                response_type=response_type,
                prefix_text="Prompt of the Moment:",
                footnote_text="forced vibe check",
                active_tags=active_tags,
            )
            if ts and state_manager and team_id:
                state_manager.get_state(team_id).set_last_prompt_ts(ts, channel=channel)
                print(f"[FORCEPROMPT] [{team_id}] Prompt ts={ts} saved to state, channel={channel}")
            respond(f"✅ Posted a prompt to {channel}.")
        except Exception as e:
            logging.exception("Error in /forceprompt")
            respond(f"❌ Failed to post prompt: {e}")

def randomize_message_block(message):
    num = random.randint(1,10)
    headerMSGs = [
        ":bangbang: NEW VIBE CHECK :bangbang:",
        ":bangbang: VIBE CHECK :bangbang:",
        ":bangbang: VIBE CHECK! :bangbang:",
        ":bangbang: VIBE CHECK ALERT :bangbang:",
        ":interrobang: NEW VIBE CHECK :interrobang:",
        ":interrobang: VIBE CHECK :interrobang:",
        ":interrobang: VIBE CHECK! :interrobang:",
        ":interrobang: VIBE CHECK ALERT :interrobang:",
        ":exclamation: NEW VIBE CHECK :exclamation:",
        ":exclamation: VIBE CHECK :exclamation:",
        ":exclamation: VIBE CHECK! :exclamation:",
        ":exclamation: VIBE CHECK ALERT :exclamation:",
    ]

    image_lists = [
        "https://media1.tenor.com/m/1CcXIDK6YboAAAAC/the-simpsons-bart.gif",
        "https://media1.tenor.com/m/hV2TZljEW1kAAAAd/vibby-vibby-vibes.gif",
        "https://media.tenor.com/y0hD2LSxx_8AAAAi/vibe.gif",
        "https://media.tenor.com/X9mVHTwAHXoAAAAi/vibes-woodstock.gif",
        "https://media1.tenor.com/m/LCpcrdtI0GYAAAAd/vibing-st6.gif",
        "https://media1.tenor.com/m/3fWNoUgRYFEAAAAd/cat-vibe-cat-meme.gif",
        "https://media1.tenor.com/m/Tfm5oTF9Xt0AAAAd/cat-sunglasses.gif",
        "https://media1.tenor.com/m/dEjkUvV_ieoAAAAC/dance-victro.gif",
        "https://media1.tenor.com/m/HCyNMWQv868AAAAC/good-night.gif",
        "https://media.tenor.com/sbfBfp3FeY8AAAAi/oia-uia.gif",
    ]
    msg_block = []
    if num <= 1:
         msg_block = [
          {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": headerMSGs[random.randint(0, len(headerMSGs) - 1)] ,
                        "emoji": True
                    },
                    "level": 2
                },
                {
                    "type": "divider"
                },
                {
                    "type": "markdown",
                    "text": message
                }
            ]
    else:
         msg_block = [
          {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": headerMSGs[random.randint(0, len(headerMSGs) - 1)],
                        "emoji": True
                    },
                    "level": 2
                },
                {
                    "type": "divider"
                },
                {
                    "type": "image",
                    "image_url": image_lists[random.randint(0, len(image_lists) - 1)],
                    "alt_text": "an image relating to the vibes."
                },
                {
                    "type": "markdown",
                    "text": message
                }
            ]
    return msg_block