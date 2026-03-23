import logging

def register_set_channel_command(bolt_app, state):
    
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
            
            state.set_active_channel(text)
            respond(f"Active channel set to {text}")
            channel = state.get_active_channel()
            client.chat_postMessage(channel=channel, text="The bot will now listen to this channel")
            
            
            
        except Exception as e:
            logging.error(f"Error in /setchannel command: {e}")
            