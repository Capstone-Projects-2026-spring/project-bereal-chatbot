from pathlib import Path
import sys

import yaml


REPO_ROOT = Path(__file__).resolve().parent
SRC_DIR = REPO_ROOT / "src"
OUTPUT_PATH = REPO_ROOT / "documentation" / "static" / "openapi.yml.yaml"

sys.path.insert(0, str(SRC_DIR))

from bot.oauth_server import flask_app  # noqa: E402


def _operation_for_rule(rule, method: str) -> dict:
    if rule.rule == "/slack/install" and method == "GET":
        return {
            "summary": "Start Slack OAuth installation",
            "description": "Redirects user to Slack OAuth authorization URL.",
            "responses": {
                "302": {"description": "Redirect to Slack OAuth authorize URL"},
            },
        }

    if rule.rule == "/slack/events" and method == "POST":
        return {
            "summary": "Receive Slack events",
            "description": "Receives Slack Events API payloads and forwards them to the Bolt handler.",
            "requestBody": {
                "required": False,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "additionalProperties": True,
                        }
                    }
                },
            },
            "responses": {
                "200": {"description": "Processed by Slack Bolt handler"},
                "400": {"description": "Bad request payload"},
                "401": {"description": "Unauthorized request"},
                "500": {"description": "Unexpected backend error"},
            },
        }

    if rule.rule == "/slack/oauth_redirect" and method == "GET":
        return {
            "summary": "Slack OAuth redirect callback",
            "description": "Exchanges OAuth code for access token and stores installation details.",
            "parameters": [
                {
                    "name": "code",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "string"},
                    "description": "Slack OAuth authorization code",
                }
            ],
            "responses": {
                "200": {"description": "Installation completed"},
                "400": {"description": "Missing or invalid OAuth code"},
            },
        }

    return {
        "summary": f"{method} {rule.rule}",
        "description": f"Auto-generated from Flask route {rule.endpoint}.",
        "responses": {
            "200": {"description": "Success"},
        },
    }


def build_openapi_schema() -> dict:
    paths: dict[str, dict] = {}

    for rule in flask_app.url_map.iter_rules():
        if rule.endpoint == "static":
            continue

        methods = sorted(m for m in rule.methods if m not in {"HEAD", "OPTIONS"})
        operations = {method.lower(): _operation_for_rule(rule, method) for method in methods}
        paths[rule.rule] = operations

    return {
        "openapi": "3.0.3",
        "info": {
            "title": "VibeCheck Backend API",
            "version": "1.0.0",
            "description": "Auto-generated from Flask route definitions in src/bot/oauth_server.py",
        },
        "servers": [
            {"url": "https://vibecheck.up.railway.app", "description": "Production"},
            {"url": "http://localhost:8080", "description": "Local"},
        ],
        "paths": paths,
    }


def main() -> None:
    schema = build_openapi_schema()
    OUTPUT_PATH.write_text(
        yaml.safe_dump(schema, sort_keys=False, allow_unicode=False),
        encoding="utf-8",
    )
    print(f"Generated OpenAPI contract at {OUTPUT_PATH}")


if __name__ == "__main__":
    main()