# src/bot/main.py
import threading

from slack_sdk import WebClient
from slack_bolt import App
from slack_bolt.authorization import AuthorizeResult
from pymongo import MongoClient

from bot.config import load_config
from bot.paths import STRUCTURED_JSONL
from bot.state import StateManager
from bot.scheduler import run_time_checker
from bot.oauth_server import run_oauth_server

from commands.force_prompt_command import register_force_prompt_command
from commands.help_command import register_help_command
from commands.status_command import register_status_command
from commands.time_commands import register_time_commands
from commands.set_channel_command import register_set_channel_command
from commands.control_panel_commands import register_control_panel
from commands.prompt_stats_command import register_prompt_stats_command
from commands.pick_topic_command import register_pick_topic_command
from commands.onboarding import register_onboarding
from commands.social_connector import register_social_connector_command
from commands.user_prompt_command import register_user_prompt_handlers
from commands.check_vibes_command import register_check_vibes_command
from commands.mentor_mentee_command import register_mentor_mentee_command
from app_logging.structured_logger import install_structured_message_logging
from services.mongo_service import init_tracker, init_user_interests
from services.prompt_service import load_prompts_df
from services.streak_service import register_streak_command


def make_authorize(cfg, mongo_uri):
    """Return a Bolt authorize callback that looks up bot tokens from MongoDB, falling back to the default token."""
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
    """Bootstrap the bot: load config, register all commands, start the scheduler thread, and serve HTTP."""
    print("\n[BOOT] Starting bot...")

    cfg = load_config()
    state_manager = StateManager()

    init_tracker(cfg.mongo_uri)
    init_user_interests(cfg.mongo_uri)
    load_prompts_df()  # pre-warm CSV cache so /picktags and /picktopic open instantly

    authorize = make_authorize(cfg, cfg.mongo_uri)
    client = WebClient(token=cfg.token)

    try:
        auth_info = client.auth_test()
        print(f"[BOOT] Bot username: @{auth_info['user']} (team: {auth_info['team']}) (Bot UserID: {auth_info['user_id']})")
    except Exception as e:
        print(f"[BOOT] Could not fetch bot username: {e}")
    bolt_app = App(authorize=authorize, signing_secret=cfg.signing_secret, ignoring_self_events_enabled=False)

    # Logging + commands
    install_structured_message_logging(bolt_app, client, cfg=cfg, log_file=str(STRUCTURED_JSONL))
    register_force_prompt_command(bolt_app, state_manager)
    register_help_command(bolt_app)
    register_status_command(bolt_app, state_manager)
    register_time_commands(bolt_app, state_manager)
    register_set_channel_command(bolt_app, state_manager)
    register_control_panel(bolt_app, state_manager)
    register_prompt_stats_command(bolt_app)
    register_pick_topic_command(bolt_app, state_manager)
    register_onboarding(bolt_app, state_manager)
    register_social_connector_command(bolt_app)
    register_user_prompt_handlers(bolt_app, state_manager)
    register_check_vibes_command(bolt_app, state_manager, auth_info['user_id'])
    register_mentor_mentee_command(bolt_app, state_manager)
    register_streak_command(bolt_app, client)

    # Online message to primary workspace
    try:
        client.chat_postMessage(channel=cfg.default_channel, text="bot online!!")
    except Exception as e:
        print(f"Error posting 'bot online' message: {e}")

    # Background time checker
    print("[BOOT] Starting background time checker...")
    time_thread = threading.Thread(
        target=run_time_checker,
        args=(state_manager, client, cfg.default_channel),
        daemon=True
    )
    time_thread.start()

    # HTTP server (main thread)
    print("[BOOT] Starting HTTP server...")
    run_oauth_server(bolt_app)


if __name__ == "__main__":
    main()
