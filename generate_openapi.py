from pathlib import Path
import sys

import yaml


REPO_ROOT = Path(__file__).resolve().parent
SRC_DIR = REPO_ROOT / "src"
OUTPUT_PATH = REPO_ROOT / "documentation" / "static" / "openapi.yml.yaml"

sys.path.insert(0, str(SRC_DIR))

from http_api.app import app  # noqa: E402


def main() -> None:
    schema = app.openapi()
    OUTPUT_PATH.write_text(
        yaml.safe_dump(schema, sort_keys=False, allow_unicode=False),
        encoding="utf-8",
    )
    print(f"Generated OpenAPI contract at {OUTPUT_PATH}")


if __name__ == "__main__":
    main()