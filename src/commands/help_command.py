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

*Other Commands*
`/forceprompt` — immediately post a random prompt to the current channel
`/forceprompt #channel-name` — post a prompt to a specific channel
`/vibestatus` — show current bot configuration
`/checkvibes` — show response data and stats for the current channel
`/picktags` — set or update your personal topic interest tags
`/connect` — set or update your personal topic interest tags
`/help` — show this message

*User-Created Prompts*
Once a day, the bot may randomly DM a channel member and invite them to write that day's prompt.
You'll have *5 minutes* to submit — pick a topic and optionally add your own custom text.
Admins can also manually assign any user as prompt creator from the *Control Panel* (App Home).

*Social Connector*
Each afternoon the bot may pair two teammates who share common interest tags and post a friendly
intro message in the main channel to help them get to know each other.
Set your interest tags with `/picktags` or during onboarding.
 
*Mentor-Mentee Program* :handshake:
The bot supports a mentor-mentee program to help teammates connect for guidance and learning:
• `/mentor signup mentor` — join as a mentor (opens a profile form)
• `/mentor signup mentee` — join as a mentee (opens a profile form)
• `/mentor status` — see your current pairing
• `/mentor leave` — leave the program
• `/mentor admin` — _(admin)_ view all profiles & manually pair users
• `/mentor match` — _(admin)_ auto-match all unmatched users by interests
""".strip()


def register_help_command(bolt_app):
    @bolt_app.command("/help")
    def handle_help(ack, respond):
        ack()
        respond(_HELP_TEXT)
