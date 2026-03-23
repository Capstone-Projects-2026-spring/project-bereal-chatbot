# src/bot/main.py
import os
import threading

from flask import Flask, request
from slack_bolt import App
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_sdk import WebClient
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.state_store import FileOAuthStateStore

from bot.config import load_config
from bot.paths import STRUCTURED_JSONL, INSTALLATIONS_DIR, STATES_DIR
from bot.state import create_state
from bot.scheduler import run_time_checker

from commands.force_prompt_command import register_force_prompt_command
from commands.time_commands import register_time_commands
from commands.set_channel_command import register_set_channel_command
from commands.control_panel_commands import register_control_panel
from app_logging.structured_logger import install_structured_message_logging


def main():
    print("\n[BOOT] Starting bot...")

    cfg = load_config()
    state = create_state(default_channel=cfg.default_channel)

    # OAuth settings — stores tokens per workspace on disk
    oauth_settings = OAuthSettings(
        client_id=cfg.client_id,
        client_secret=cfg.client_secret,
        scopes=["chat:write", "channels:history", "channels:read", "commands"],
        installation_store=FileInstallationStore(base_dir=str(INSTALLATIONS_DIR)),
        state_store=FileOAuthStateStore(
            expiration_seconds=600,
            base_dir=str(STATES_DIR)
        ),
    )

    bolt_app = App(
        signing_secret=cfg.signing_secret,
        oauth_settings=oauth_settings,
    )

    # Primary client for scheduler/startup messages (uses the single bot token)
    client = WebClient(token=cfg.token)

    # Register all handlers
    install_structured_message_logging(bolt_app, client, log_file=str(STRUCTURED_JSONL))
    register_force_prompt_command(bolt_app, client)
    register_time_commands(bolt_app, state)
    register_set_channel_command(bolt_app, client, state)
    register_control_panel(bolt_app, state)

    print("[BOOT] Bot ready.")

    # Background scheduler (runs for primary workspace)
    print("[BOOT] Starting background time checker...")
    time_thread = threading.Thread(
        target=run_time_checker,
        args=(client, cfg.default_channel, state),
        daemon=True
    )
    time_thread.start()

    # Flask web server
    flask_app = Flask(__name__)
    handler = SlackRequestHandler(bolt_app)

    @flask_app.route("/slack/events", methods=["POST"])
    def slack_events():
        return handler.handle(request)

    @flask_app.route("/slack/install", methods=["GET"])
    def slack_install():
        return handler.handle(request)

    @flask_app.route("/slack/oauth_redirect", methods=["GET"])
    def slack_oauth_redirect():
        return handler.handle(request)

    @flask_app.route("/health", methods=["GET"])
    def health():
        return "ok", 200

    port = int(os.environ.get("PORT", 3000))
    print(f"[BOOT] Starting Flask on port {port}...")
    flask_app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
