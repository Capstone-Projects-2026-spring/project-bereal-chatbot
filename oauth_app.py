import hashlib
import hmac
import json
import os
import secrets
import sys
import time
from pathlib import Path
from typing import Dict, Tuple
from urllib.parse import urlencode

from flask import Flask, jsonify, redirect, request
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Put src/ on path so bot modules are importable
REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "src"))

app = Flask(__name__)

STATE_TTL_SECONDS = 600
INSTALLATIONS_DIR = Path("data/installations")
BOLT_HANDLER = None
BOLT_INIT_ERROR = None


def _get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _state_secret() -> str:
    return os.getenv("SLACK_SIGNING_SECRET") or _get_env("SLACK_CLIENT_SECRET")


def _create_state() -> str:
    timestamp = str(int(time.time()))
    nonce = secrets.token_urlsafe(16)
    payload = f"{timestamp}.{nonce}"
    signature = hmac.new(
        _state_secret().encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return f"{payload}.{signature}"


def _validate_state(state: str) -> bool:
    try:
        timestamp_str, nonce, provided_sig = state.split(".", 2)
        timestamp = int(timestamp_str)
    except (ValueError, AttributeError):
        return False

    now = int(time.time())
    if now - timestamp > STATE_TTL_SECONDS:
        return False

    payload = f"{timestamp}.{nonce}"
    expected_sig = hmac.new(
        _state_secret().encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_sig, provided_sig)


def _save_installation(oauth_response: dict) -> None:
    team = oauth_response.get("team") or {}
    team_id = team.get("id") or "unknown"
    INSTALLATIONS_DIR.mkdir(parents=True, exist_ok=True)
    out_file = INSTALLATIONS_DIR / f"{team_id}.json"
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(oauth_response, f, indent=2)


@app.get("/health")
def health() -> Tuple[Dict[str, bool], int]:
    return {"ok": True}, 200


@app.get("/slack/install")
def slack_install():
    client_id = _get_env("SLACK_CLIENT_ID")
    redirect_uri = _get_env("SLACK_REDIRECT_URI")
    scopes = _get_env("SLACK_BOT_SCOPES")

    state = _create_state()
    query = urlencode(
        {
            "client_id": client_id,
            "scope": scopes,
            "redirect_uri": redirect_uri,
            "state": state,
        }
    )
    auth_url = f"https://slack.com/oauth/v2/authorize?{query}"
    return redirect(auth_url, code=302)


@app.get("/slack/oauth_redirect")
def slack_oauth_redirect():
    error = request.args.get("error")
    if error:
        return jsonify({"ok": False, "error": error}), 400

    code = request.args.get("code")
    state = request.args.get("state")

    if not code or not state:
        return jsonify({"ok": False, "error": "missing_code_or_state"}), 400

    if not _validate_state(state):
        return jsonify({"ok": False, "error": "invalid_or_expired_state"}), 400

    client_id = _get_env("SLACK_CLIENT_ID")
    client_secret = _get_env("SLACK_CLIENT_SECRET")
    redirect_uri = _get_env("SLACK_REDIRECT_URI")

    try:
        client = WebClient()
        response = client.oauth_v2_access(
            client_id=client_id,
            client_secret=client_secret,
            code=code,
            redirect_uri=redirect_uri,
        )
        oauth_data = response.data if hasattr(response, "data") else dict(response)
        _save_installation(oauth_data)

        # DM the installer a welcome message
        bot_token = oauth_data.get("access_token")
        installer_id = (oauth_data.get("authed_user") or {}).get("id")
        if bot_token and installer_id:
            try:
                WebClient(token=bot_token).chat_postMessage(
                    channel=installer_id,
                    text=(
                        "*VibeCheck is installed!*\n\n"
                        "Use `/setchannel #your-channel` let me know where you want the app to operate.\n"
                        "Then open the App Home in our DMs tab to configure the schedule."
                    )
                )
            except Exception:
                pass  # Don't fail the install if the DM fails

    except SlackApiError as e:
        return jsonify({"ok": False, "error": e.response.get("error", "oauth_failed")}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

    return (
        "VibeCheck installed successfully. You can close this tab and return to Slack.",
        200,
    )


def _init_bolt():
    global BOLT_HANDLER, BOLT_INIT_ERROR
    try:
        from bot.main import create_bolt_app
        from slack_bolt.adapter.flask import SlackRequestHandler
        bolt = create_bolt_app()
        BOLT_HANDLER = SlackRequestHandler(bolt)
        BOLT_INIT_ERROR = None

        print("[BOOT] Bolt handlers registered.")
    except Exception as e:
        BOLT_HANDLER = None
        BOLT_INIT_ERROR = str(e)
        print(f"[BOT] Failed to init bolt: {e}")


@app.route("/slack/events", methods=["POST"])
def slack_events():
    payload = request.get_json(silent=True) or {}
    if payload.get("type") == "url_verification":
        return jsonify({"challenge": payload.get("challenge", "")}), 200

    if BOLT_HANDLER is None:
        return jsonify({"ok": False, "error": "bolt_not_initialized", "details": BOLT_INIT_ERROR}), 503

    return BOLT_HANDLER.handle(request)


@app.route("/slack/interactions", methods=["POST"])
def slack_interactions():
    if BOLT_HANDLER is None:
        return jsonify({"ok": False, "error": "bolt_not_initialized", "details": BOLT_INIT_ERROR}), 503

    return BOLT_HANDLER.handle(request)


_init_bolt()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "3000"))
    app.run(host="0.0.0.0", port=port)
