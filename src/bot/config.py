# src/bot/config.py
import os
from dataclasses import dataclass
from dotenv import load_dotenv

from bot.paths import REPO_ROOT


@dataclass(frozen=True)
class BotConfig:
    token: str
    app_token: str
    default_channel: str
    mongo_uri: str


def load_config() -> BotConfig:
    env_path = REPO_ROOT / ".env"
    load_dotenv(dotenv_path=env_path)
    print("Loaded .env from:", env_path)

    token = os.getenv("SLACK_BOT_TOKEN")
    app_token = os.getenv("SLACK_APP_TOKEN")
    default_channel = os.getenv("DEFAULT_CHANNEL", "#bot-test")
    mongo_uri = os.getenv("MONGO_URI")

    if not token:
        raise RuntimeError("Missing SLACK_BOT_TOKEN in .env")
    if not app_token:
        raise RuntimeError("Missing SLACK_APP_TOKEN in .env")
    if not mongo_uri:
        raise RuntimeError("Missing MONGO_URI in .env")

    return BotConfig(token=token, app_token=app_token, default_channel=default_channel, mongo_uri=mongo_uri)