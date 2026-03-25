# src/commands/help_command.py

_HELP_TEXT = """
*Vibe Check Bot — Setup & Usage Guide*

*Step 1: Add the bot to your channel*
Go to the channel you want the bot to post in and type:
`/invite @VibeCheck`
The bot must be a member of the channel before it can post there.

*Step 2: Set the active channel*
Run this command in any channel:
`/setchannel #your-channel-name`
This tells the bot where to send daily prompts.

*Step 3: Configure the bot via the Control Panel*
Open the bot's *App Home* tab (click the bot's name in the sidebar).
From there you can:

• *Mode* — choose how the daily prompt time is picked:
  - *Random Time* — picks a random time within your start/end range each day
  - *Preset Time Select* — pick from a list of preset times
  - *Static Set Time* — type in a specific time that repeats every day

• *Random Time Range* — set the start and end window for random mode (e.g. `09:30:00 AM` to `05:00:00 PM`)

• *Preset Times* — select a fixed time from the dropdown

• *Static Set Time* — type an exact time in `HH:MM:SS AM/PM` format (e.g. `03:00:00 PM`)

• *Active Days* — check the days you want the bot to post (uncheck days to skip them)

*Other Commands*
`/forceprompt` — immediately post a random prompt to the current channel
`/forceprompt #channel-name` — post a prompt to a specific channel
`/setchannel #channel-name` — change the active channel
`/help` — show this message
""".strip()


def register_help_command(bolt_app):
    @bolt_app.command("/help")
    def handle_help(ack, respond):
        ack()
        respond(_HELP_TEXT)
