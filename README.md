<div align="center">

# VibeCheck
[![Report Issue on Jira](https://img.shields.io/badge/Report%20Issues-Jira-0052CC?style=flat&logo=jira-software)](https://temple-cis-projects-in-cs.atlassian.net/jira/software/c/projects/DT/issues)
[![Deploy Docs](https://github.com/ApplebaumIan/tu-cis-4398-docs-template/actions/workflows/deploy.yml/badge.svg)](https://github.com/ApplebaumIan/tu-cis-4398-docs-template/actions/workflows/deploy.yml)
[![Documentation Website Link](https://img.shields.io/badge/-Documentation%20Website-brightgreen)](https://capstone-projects-2026-spring.github.io/project-bereal-chatbot/)


</div>


## Keywords

Section 1, chatbot application, Python, MongoDB, Railway, Slack Bolt, FastAPI, social connection, future of work 

## Project Abstract

This project presents the design and implementation of a BeReal-inspired chatbot integrated within Slack that aims to form social connections in both professional and academic environments. Vibecheck operates entirely within a messaging platform, allowing users to share short, but time-restricted updates about their day during breaks, such as lunch periods. Users interact with the chatbot through Slack messages, buttons, bot commands, image uploads that enables users to submit photos with captions, or just text in response to daily prompts.

The system is built using Python and processes Slack events through the Slack API. MongoDB is used to persist user data, prompts, submissions, timestamps, and late flags, enabling consistent tracking and retrieval of shared content. Communication occurs between Slack and the backend, where Slack acts as the user interface and the FastAPI service serves as the application logic layer.

## High Level Requirement

VibeCheck is a chatbot that uses messaging platforms to operate. It sends prompts that will have a timed response others will reply to. Once sent, users can see each other's posts and responses. It is a Slack-integrated chatbot designed to encourage social interaction within professional or academic environments. The chatbot periodically sends time-limited prompts to users during designated break periods, such as lunch breaks. Users respond to these prompts by submitting short text updates and optional images with captions directly through Slack.

Interaction with VibeCheck occurs entirely within Slack channels using standard messaging features and bot commands. Once a response window closes, users are able to view each other’s submissions within the same channel, promoting sociability while maintaining a professional tone. The system automatically enforces timing constraints, manages submissions, and provides feedback to users without requiring a separate application or external interface.

## Conceptual Design

VibeCheck follows a client–server, event-driven architecture. Slack serves as the user interaction layer, where users receive prompts and submit responses. Python is the backend that validates incoming requests, applies business rules such as submission deadlines, processes text and image data, and sends responses back to Slack. Persistent data is stored in database. Stored data includes user data, daily prompts, submissions, timestamps, and late submission flags. This project is designed to run in Slack.

## Background 

Social check-in applications such, as BeReal, encourages authenticity and breaking down superficial barriers. This is done by having users take a time-bounded photo of what they're doing and of themselves, but they are primarily designed for mobile and personal social contexts. VibeCheck adapts this concept to professional and academic environments by providing similar functionalities within Slack. Unlike BeReal, which relies on a dedicated mobile frontend, VibeCheck operates entirely through an existing messaging interface, reducing friction and encouraging participation during natural breaks in the workday.

## Required Resources

To develop VibeCheck, background knowledge in Python, APIs, databases is necessary, along with familiarity with event-driven application design. Software resources include Python, any IDE, and access to Slack.

No hardware requirements. Resources are commonly available within standard Computer Science department environments.

## How to Run the Project

Follow these steps to set up and run VibeCheck in your own Slack workspace.

### 1. Slack App Setup

Go to the Slack developer portal: https://api.slack.com/apps

**Create and configure the Slack app:**

1. Click **Create New App** → choose **From scratch**.
2. Enter an app name and select the Slack workspace where you want to install it.
3. In the app settings, open **Socket Mode** and turn on **Enable Socket Mode**.
4. In **Basic Information**, create an app-level token with the `connections:write` scope. Save the generated token (starts with `xapp-`) as `SLACK_APP_TOKEN`.
5. Also in **Basic Information**, copy the **Signing Secret** and save it as `SLACK_SIGNING_SECRET`.
6. Open **OAuth & Permissions**. Under **Bot Token Scopes**, add the following scopes:
   - `chat:write` — send messages as the bot
   - `chat:write.public` — post in channels without being invited
   - `commands` — register and respond to slash commands
   - `channels:read` — list channels and look up channel info
   - `channels:history` — read messages in public channels
   - `im:write` — open and send direct messages
   - `im:history` — read messages in DMs
   - `mpim:write` — create and post to group DMs (used for mentor-mentee group chats)
   - `reactions:read` — read emoji reactions on messages
   - `users:read` — look up user profile information
   - `app_mentions:read` — receive events when the bot is mentioned
7. Under **Redirect URLs**, add your redirect URI (e.g. `https://your-host/slack/oauth_redirect`) and save it as `SLACK_REDIRECT_URI`.
8. Click **Install App to Workspace**.
9. Copy the bot token (starts with `xoxb-`) and save it as `SLACK_BOT_TOKEN`.
10. From the **Basic Information** page, copy the **Client ID** and **Client Secret** and save them as `SLACK_CLIENT_ID` and `SLACK_CLIENT_SECRET`.

**Register Slash Commands:**

In your app settings, go to **Slash Commands** and add each of the following. Set the **Request URL** to your hosted bot URL (e.g. `https://your-host/slack/events`) for each one — or leave it blank if you are using Socket Mode.

| Command | Description |
|---|---|
| `/help` | Show setup guide and list of all commands |
| `/setchannel` | Set the channel where daily prompts are posted (e.g. `/setchannel #general`) |
| `/forceprompt` | Immediately post a vibe check prompt; optionally pass `text`, `image`, or `#channel` |
| `/vibestatus` | Display the current bot configuration for this workspace |
| `/checkvibes` | Show response stats and submission data for the current channel |
| `/picktags` | Set your personal interest tags used for social matching and prompt filtering |
| `/picktopic` | Set a topic so the next prompt is drawn from that category |
| `/picktime` | Manually pick a time slot number (1–11) for today's prompt |
| `/findtime` | Show the currently scheduled prompt time and active mode |
| `/connect` | Update your interest profile for social connector matching |
| `/streak` | View your current vibe check response streak |
| `/promptstats` | Show stats on prompts that have been sent (admin use) |
| `/mentor` | Mentor-mentee program — use `signup mentor`, `signup mentee`, `status`, `leave`, `admin`, or `match` |

---

### 2. Groq API Key Setup

Go to the Groq console: https://console.groq.com/

1. Sign in or create an account.
2. Open the **API Keys** section and create a new key.
3. Copy the key and save it as `GROQ_API_KEY`.

---

### 3. MongoDB Setup

1. Create a free cluster at https://www.mongodb.com/atlas
2. Create a database user and allow access from your IP (or `0.0.0.0/0` for open access).
3. Copy the connection string and save it as `MONGO_URI`.

---

### 4. Create your `.env` file

Create a `.env` file in the project root with the following variables:

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

---

### 5. Run the Bot

Install dependencies and start the bot:

```bash
pip install -r requirements.txt
python src/app.py
```

You should see:

```
⚡️ Bolt app is running in Socket Mode!
```

Use the slash command `/help` in any channel where the bot is present to see all available commands.

## Contact Information
To reach out for any questions, comments, or concerns regarding this project, you can contact me via email or text:

Khai: tuq43307@temple.edu | 267-241-3304


## Running Tests

Run test commands from the project root directory.

1. Install development dependencies:

    `python -m pip install -r requirements-dev.txt`

2. Run all unit tests:

    `python run_tests.py`

Optional:

- Run a specific file: `python run_tests.py tests/test_commands.py`
- Verbose output: `python run_tests.py -v`
- Run acceptance tests only: `pytest -m acceptance`
- Run all tests with pytest directly: `pytest`

## CI/CD with GitHub Actions

Added a new workflow in file `.github/workflows/ci-tests.yml`. Tests are executed by `python run_tests.py` and runs automatically on every `push` and `pull_request`.

[Dependencies installed from `requirements-dev.txt`]


To view results:

1. Click the `Actions` tab.
2. Open the latest `Python CI Tests` run.

## Collaborators

<div align="center">

[//]: # (Replace with your collaborators)
[Justin Pham](https://github.com/Prismfade) • [Khai Thach](https://github.com/Khai-Thach) • [John Livezey](https://github.com/Jawn654) • [Chris Breeden](https://github.com/CRBreeden) • [Nathan Hollick](https://github.com/tup40793) • [Carl Pierre-Louis](https://github.com/carlpielou03)

</div>
