---
sidebar_position: 5
---

# User's Manual

VibeCheck is a BeReal-inspired Slack bot that sends daily prompts to your workspace and connects team members with shared interests.

---

## Quick Start Guide

Once the bot is in your workspace:

1. Run `/help` to see all available commands.
2. Run `/setchannel #your-channel` to pick where prompts get posted.
3. Run `/picktags` to set your interest tags.
4. Run `/vibestatus` to check the bot setup.

The bot will post a daily prompt to the channel you set. Reply in-thread when it goes out.

---

## Installation

### Prerequisites

- A Slack workspace where you have permission to install apps
- A MongoDB Atlas account
- A Groq API account
- Python 3.8 or higher

### Step 1: Slack App Setup

Go to https://api.slack.com/apps and create a new app.

1. Click **Create New App** -> create **From scratch**.
2. Enter an app name and select your Slack workspace.
3. Open program in **Socket Mode** and enable it.
4. In **Basic Information**, create an app-level token with the `connections:write` scope. Save it as `SLACK_APP_TOKEN` (starts with `xapp-`).
5. Copy the **Signing Secret** from **Basic Information** and save it as `SLACK_SIGNING_SECRET`.
6. Open **OAuth & Permissions** and add the following **Bot Token Scopes**:

| Scope | Purpose |
|---|---|
| `chat:write` | Send messages as the bot |
| `chat:write.public` | Post in channels without being invited |
| `commands` | Register and respond to slash commands |
| `channels:read` | List and look up channels |
| `channels:history` | Read messages in public channels |
| `im:write` | Open and send direct messages |
| `im:history` | Read messages in DMs |
| `mpim:write` | Create and post to group DMs (mentor program) |
| `reactions:read` | Read emoji reactions on messages |
| `users:read` | Look up user profile information |
| `app_mentions:read` | Receive events when the bot is mentioned |

7. Under **Redirect URLs**, add your redirect URI (e.g. `https://your-host/slack/oauth_redirect`) and save it as `SLACK_REDIRECT_URI`.
8. Click **Install App to Workspace**.
9. Copy the **Bot Token** (starts with `xoxb-`) and save it as `SLACK_BOT_TOKEN`.
10. Copy the **Client ID** and **Client Secret** from **Basic Information** and save them as `SLACK_CLIENT_ID` and `SLACK_CLIENT_SECRET`.

### Step 2: Register Slash Commands

In your app settings, go to **Slash Commands** and register each of the following:

| Command | Description |
|---|---|
| `/help` | Show setup guide and list of all commands |
| `/setchannel` | Set the channel where daily prompts are posted |
| `/forceprompt` | Immediately post a vibe check prompt |
| `/vibestatus` | Display the current bot configuration |
| `/checkvibes` | Show response stats for the current channel |
| `/picktags` | Set your personal interest tags |
| `/picktopic` | Set a topic for the next prompt |
| `/picktime` | Manually pick a time slot (1–17) for today's prompt |
| `/findtime` | Show the currently scheduled prompt time and mode |
| `/connect` | Run the social connector to match users by shared tags |
| `/streak` | View your current vibe check response streak |
| `/promptstats` | Show prompt send statistics (admin use) |
| `/mentor` | Mentor-mentee program commands |

### Step 3: Groq API Key

Go to https://console.groq.com/, create an API key, and save it as `GROQ_API_KEY`.

### Step 4: MongoDB Setup

1. Create a free cluster at https://www.mongodb.com/atlas.
2. Create a database user and allow network access from your server's IP.
3. Copy the connection string and save it as `MONGO_URI`.

### Step 5: Create the `.env` File

Create a `.env` file in the project root:

```
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_CLIENT_ID=your-client-id
SLACK_CLIENT_SECRET=your-client-secret
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_REDIRECT_URI=https://your-host/slack/oauth_redirect
MONGO_URI=mongodb+srv://your-connection-string
GROQ_API_KEY=your-groq-api-key
```

### Step 6: Run the Bot

```bash
pip install -r requirements.txt
python src/app.py
```

You should see:

```
⚡️ Bolt app is running in Socket Mode!
```

### Uninstalling

To remove the bot from a workspace, go to your Slack workspace settings -> **Apps** -> find VibeCheck -> **Remove App**. To fully remove from apps, delete the app at https://api.slack.com/apps and shut down where the server is running.

---

## Configuration

### Setting the Prompt Channel

Use `/setchannel #channel-name` to set which channel receives daily prompts. Only one channel is active per workspace at a time.


### Collections

| Collection | Contents |
|---|---|
| `installations` | OAuth install records per workspace |
| `workspace_state` | Per-workspace configuration (channel, mode, time, active days) |
| `user_interests` | User interest tags used for social matching |
| `prompts` | Prompt library with topic categories |
| `prompt_tracker` | Record of prompts sent and response counts |
| `streaks` | Per-user response streak data |
| `mentor_profiles` | Mentor-mentee signup records and pairings |

## Application Functions

### User Commands

| Command | What it does |
|---|---|
| `/picktags` | Pick your interest tags |
| `/connect` | Get matched with someone who shares your interests |
| `/streak` | See your response streak and the leaderboard |
| `/checkvibes` | See who responded to today's prompt |
| `/mentor signup mentor` | Sign up as a mentor |
| `/mentor signup mentee` | Sign up as a mentee |
| `/mentor status` | Check your mentor pairing status |
| `/mentor leave` | Leave the mentor program |
| `/help` | See all commands |

### Admin Commands

| Command | What it does |
|---|---|
| `/setchannel #channel` | Set the channel where prompts are posted |
| `/forceprompt` | Post a prompt right now |
| `/forceprompt #channel` | Post a prompt to a specific channel |
| `/picktime [1-17]` | Set the prompt time slot for today |
| `/findtime` | Check the current scheduled time and mode |
| `/vibestatus` | See the full bot config for this workspace |
| `/picktopic [topic]` | Set the topic for the next prompt |
| `/promptstats` | See prompt history and response counts |
| `/mentor match` | Pair up mentors and mentees |
| `/mentor admin` | See the mentor program summary |


## Support

To report a bug, open an issue on the project Jira board:
https://temple-cis-projects-in-cs.atlassian.net/jira/software/c/projects/DT/issues
