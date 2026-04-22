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

Join the Slack workspace: [VibeCheck Bot Team](https://join.slack.com/t/vibecheckbotteam/shared_invite/zt-3tdl9nbvm-dKMeo~DRH4KJoJbDhVQgFw)

You can also add the chatbot to your own workspace: [VibeCheck Bot](https://worker-production-234c.up.railway.app/slack/install) 


Running the chatbot locally is not necessary, since it is already deployed on Railway. Use the slash command "/help" in # bot-test channel to see what the bot can do and check out the docusaurus for additional details.

If you still want to run the chatbot locally, here are the following instructions:

1. Prerequisites

    - Python 3.10+
    - Access to a Slack workspace where you can configure an app
    - A MongoDB connection string
    - Optional: `GROQ_API_KEY` for LLM-powered reactions/features

2. Clone the repo and open it

    `git clone https://github.com/capstone-projects-2026-spring/project-bereal-chatbot.git`

    `cd project-bereal-chatbot`

3. Create and activate a virtual environment

    Windows (PowerShell):
    `python -m venv .venv`
    `.\.venv\Scripts\Activate.ps1`

    macOS/Linux:
    `python3 -m venv .venv`
    `source .venv/bin/activate`

4. Install dependencies

    `python -m pip install -r requirements-dev.txt`

5. Create a `.env` file in the project root with at least:

    `SLACK_BOT_TOKEN=your_xoxb_token`
    `SLACK_SIGNING_SECRET=your_signing_secret`
    `MONGO_URI=your_mongodb_connection_string`

    Optional values:
    `DEFAULT_CHANNEL=#bot-test`
    `PORT=8080`
    `GROQ_API_KEY=your_groq_api_key`
    `LLM_REACTIONS_ENABLED=true`
    `LLM_REACTIONS_PROBABILITY=0.5`

6. Start the bot

    `python run.py`

7. Expose your local server to Slack (required for local event callbacks)

    Use a tunnel such as ngrok or Cloudflare Tunnel and map it to your local bot port (default 8080).

8. Configure your Slack app URLs

    Set Request URL for Event Subscriptions to:
    `https://<your-public-url>/slack/events`

    If using OAuth install flow, also configure:
    `https://<your-public-url>/slack/oauth_redirect`

9. Verify in Slack

    Run `/help` in your test channel. If the bot responds, your local setup is working.

Any and all critiques will be greatly appreciated. Have fun testing! 🙂

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
