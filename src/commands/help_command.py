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
`/connect` — run the social connector now in the current channel
`/setchannel #channel-name` — change the active channel
`/vibestatus` — show current bot configuration
`/picktags` — set or update your personal topic interest tags
`/connect` — set or update your personal topic interest tags
`/help` — show this message

*User-Created Prompts*
Once a day, the bot may randomly DM a channel member and invite them to write that day's prompt.
You'll have *5 minutes* to submit — pick a topic (required) and optionally add your own custom text.
Admins can also manually assign any user as prompt creator from the *Control Panel* (App Home).

*Social Connector*
Each afternoon the bot may pair two teammates who share common interest tags and post a friendly
intro message in the main channel to help them get to know each other.
Set your interest tags with `/picktags` or during onboarding.
""".strip()


def register_help_command(bolt_app):
    @bolt_app.command("/help")
    def handle_help(ack, respond):
        ack()
        respond(_HELP_TEXT)
