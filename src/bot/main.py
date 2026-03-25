# src/bot/main.py
import threading

from slack_sdk import WebClient
from slack_bolt import App
from slack_bolt.authorization import AuthorizeResult
from pymongo import MongoClient

from bot.config import load_config
from bot.paths import STRUCTURED_JSONL
from bot.state import create_state
from bot.scheduler import run_time_checker
from bot.oauth_server import run_oauth_server

from commands.force_prompt_command import register_force_prompt_command
from commands.help_command import register_help_command
from commands.time_commands import register_time_commands
from commands.set_channel_command import register_set_channel_command
from commands.control_panel_commands import register_control_panel
from app_logging.structured_logger import install_structured_message_logging


def make_authorize(cfg, mongo_uri):
    mongo_client = MongoClient(mongo_uri)
    installations = mongo_client["vibecheck"]["installations"]

    def authorize(enterprise_id, team_id, **kwargs):
        try:
            query = {"team_id": team_id}
            if enterprise_id:
                query["enterprise_id"] = enterprise_id
            record = installations.find_one(query)
            if record:
                return AuthorizeResult.from_auth_test_response(
                    auth_test_response=WebClient(token=record["bot_token"]).auth_test(),
                    bot_token=record["bot_token"],
                )
            return AuthorizeResult.from_auth_test_response(
                auth_test_response=WebClient(token=cfg.token).auth_test(),
                bot_token=cfg.token,
            )
        except Exception as e:
            print(f"[AUTHORIZE] ERROR: {e}")
            return AuthorizeResult.from_auth_test_response(
                auth_test_response=WebClient(token=cfg.token).auth_test(),
                bot_token=cfg.token,
            )

    return authorize


def main():
    print("\n[BOOT] Starting bot...")

    cfg = load_config()
    state = create_state(default_channel=cfg.default_channel)

    authorize = make_authorize(cfg, cfg.mongo_uri)
    client = WebClient(token=cfg.token)
    bolt_app = App(authorize=authorize, signing_secret=cfg.signing_secret, ignoring_self_events_enabled=False)

    # Logging + commands
    install_structured_message_logging(bolt_app, client, log_file=str(STRUCTURED_JSONL))
    register_force_prompt_command(bolt_app)
    register_help_command(bolt_app)
    register_time_commands(bolt_app, state)
    register_set_channel_command(bolt_app, state)
    register_control_panel(bolt_app, state)

    # Online message
    active_channel = state.get_active_channel() or cfg.default_channel
    try:
        client.chat_postMessage(channel=active_channel, text="bot online")
    except Exception as e:
        print(f"Error posting 'bot online' message: {e}")

    # Background time checker
    print("[BOOT] Starting background time checker...")
    time_thread = threading.Thread(
        target=run_time_checker,
        args=(client, cfg.default_channel, state),
        daemon=True
    )
    time_thread.start()

    # HTTP server (main thread)
    print("[BOOT] Starting HTTP server...")
    run_oauth_server(bolt_app)


if __name__ == "__main__":
    main()