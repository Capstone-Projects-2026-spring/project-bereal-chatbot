import logging
from bot.state import get_team_id


def register_set_channel_command(bolt_app, state_manager):

    @bolt_app.command("/setchannel")
    def handle_setchannel_command(ack, respond, body, client):
        try:
            ack()
            text = body.get("text", "").strip()
            if not text:
                respond("Please provide a channel name using `/setchannel #channel-name`")
                return

            if not text.startswith("#"):
                respond("Please provide a valid channel name starting with `#`")
                return

            team_id = get_team_id(body)
            state = state_manager.get_state(team_id)
            state.set_active_channel(text)
            state.set_active_token(client.token)
            respond(f"Active channel set to {text}")
            client.chat_postMessage(channel=text, text="The bot will now listen to this channel")

        except Exception as e:
            logging.error(f"Error in /setchannel command: {e}")
