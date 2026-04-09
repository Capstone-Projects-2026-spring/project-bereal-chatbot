# src/bot/oauth_server.py
import os
import requests
from datetime import datetime
from flask import Flask, request, redirect
from pymongo import MongoClient
from slack_bolt.adapter.flask import SlackRequestHandler

flask_app = Flask(__name__)

SLACK_CLIENT_ID = os.getenv("SLACK_CLIENT_ID")
SLACK_CLIENT_SECRET = os.getenv("SLACK_CLIENT_SECRET")
MONGO_URI = os.getenv("MONGO_URI")

_bolt_handler = None

_mongo_client = None

def get_db():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(MONGO_URI)
    return _mongo_client["vibecheck"]["installations"]


@flask_app.route("/slack/install")
def install():
    scopes = "chat:write,channels:history,groups:history,im:history,mpim:history,commands,reactions:write"
    url = (
        f"https://slack.com/oauth/v2/authorize"
        f"?client_id={SLACK_CLIENT_ID}"
        f"&scope={scopes}"
        f"&redirect_uri={os.getenv('SLACK_REDIRECT_URI')}"
    )
    return redirect(url)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return _bolt_handler.handle(request)


@flask_app.route("/slack/oauth_redirect")
def oauth_redirect():
    code = request.args.get("code")
    if not code:
        return "Missing code", 400

    response = requests.post("https://slack.com/api/oauth.v2.access", data={
        "client_id": SLACK_CLIENT_ID,
        "client_secret": SLACK_CLIENT_SECRET,
        "code": code,
        "redirect_uri": os.getenv("SLACK_REDIRECT_URI"),
    })

    data = response.json()
    if not data.get("ok"):
        return f"OAuth failed: {data.get('error')}", 400

    # Save installation to MongoDB
    collection = get_db()
    collection.update_one(
        {"team_id": data["team"]["id"]},
        {"$set": {
            "team_id": data["team"]["id"],
            "team_name": data["team"]["name"],
            "bot_token": data["access_token"],
            "bot_user_id": data.get("bot_user", {}).get("id"),
            "installed_by_user_id": data.get("authed_user", {}).get("id"),
            "installed_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        }},
        upsert=True
    )

    return "App installed successfully! You can close this tab and start using the bot in Slack."


def run_oauth_server(bolt_app):
    global _bolt_handler
    _bolt_handler = SlackRequestHandler(bolt_app)
    port = int(os.getenv("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)
