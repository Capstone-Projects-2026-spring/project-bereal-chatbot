import slack
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

token = os.getenv("SLACK_TOKEN")
print("Loaded .env from:", env_path)
print("test")
client = slack.WebClient(token=token)

client.chat_postMessage(channel="#bot-test", text="Hello from Python!")