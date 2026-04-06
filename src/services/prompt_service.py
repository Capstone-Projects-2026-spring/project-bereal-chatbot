# src/services/prompt_service.py
from __future__ import annotations

import random
from datetime import datetime
from typing import Optional, Tuple

import pandas as pd

from bot.paths import PROMPTS_CSV


# Cache the dataframe so we don't reread the CSV constantly
_PROMPTS_DF = None


def load_prompts_df(force_reload: bool = False) -> pd.DataFrame:
    """
    Load prompts CSV into a DataFrame. Caches in memory unless force_reload=True.
    CSV is expected at data/prompts/vibecheck_prompts.csv (see bot.paths).
    """
    global _PROMPTS_DF

    if _PROMPTS_DF is not None and not force_reload:
        return _PROMPTS_DF

    csv_path = PROMPTS_CSV

    if not csv_path.exists():
        raise FileNotFoundError(f"Could not find CSV at: {csv_path}")

    df = pd.read_csv(csv_path)

    # Normalize columns (helpful if your CSV is slightly inconsistent)
    df.columns = [c.strip() for c in df.columns]

    # Common expected columns (we'll be flexible):
    # - prompt_id or id
    # - prompt_text or text or prompt
    # - response_type (optional)
    # - asked_at / last_asked_at (optional)
    _PROMPTS_DF = df
    return df


def _get_col(df: pd.DataFrame, candidates) -> Optional[str]:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def get_random_prompt(response_type: Optional[str] = None) -> dict:
    """
    Returns a random row (as dict). If response_type is provided, filter on it when possible.
    """
    df = load_prompts_df()

    # Identify column names flexibly
    id_col = _get_col(df, ["prompt_id", "id"])
    text_col = _get_col(df, ["prompt_text", "text", "prompt"])
    type_col = _get_col(df, ["response_type", "type"])

    if text_col is None:
        raise RuntimeError(
            f"CSV at {PROMPTS_CSV} must contain a prompt text column "
            f"(expected one of: prompt_text, text, prompt). Found: {list(df.columns)}"
        )

    filtered = df

    # Filter by response_type only if the CSV has that column
    if response_type and type_col:
        filtered = df[df[type_col].astype(str).str.lower() == str(response_type).lower()]

        # If filtering results in nothing, fall back to full df
        if filtered.empty:
            filtered = df

    row = filtered.sample(n=1).iloc[0].to_dict()

    # Ensure there's always an id even if the CSV doesn't have one
    if not id_col:
        # create a stable-ish id from index if needed
        row["prompt_id"] = int(filtered.sample(n=1).index[0])

    # Normalize keys
    if id_col and id_col != "prompt_id":
        row["prompt_id"] = row[id_col]
    if text_col and text_col != "prompt_text":
        row["prompt_text"] = row[text_col]

    return row


def get_random_prompt_text(response_type: Optional[str] = None, active_tags: Optional[set] = None) -> Tuple[str, str, str]:
    """
    Returns (prompt_id, prompt_text, tags).
    If active_tags is a non-empty set, only prompts whose tags overlap with it are considered.
    """
    df = load_prompts_df()
    tags_col = _get_col(df, ["tags", "tag"])

    if active_tags and tags_col:
        mask = df[tags_col].astype(str).apply(
            lambda cell: any(t.strip().lower() in {a.lower() for a in active_tags} for t in cell.split(","))
        )
        filtered = df[mask]
        if filtered.empty:
            filtered = df  # fall back to all prompts if filter matches nothing
        row = filtered.sample(n=1).iloc[0].to_dict()
        id_col = _get_col(filtered, ["prompt_id", "id"])
        text_col = _get_col(filtered, ["prompt_text", "text", "prompt"])
        if id_col and id_col != "prompt_id":
            row["prompt_id"] = row[id_col]
        if text_col and text_col != "prompt_text":
            row["prompt_text"] = row[text_col]
        if not id_col:
            row["prompt_id"] = str(filtered.sample(n=1).index[0])
    else:
        row = get_random_prompt(response_type=response_type)

    tags = str(row.get(tags_col, "")) if tags_col else ""
    return str(row["prompt_id"]), str(row["prompt_text"]), tags


def get_available_topics() -> list[str]:
    """
    Returns the hardcoded list of available topic interest tags.
    These are purely for user interest tracking and do not affect prompt selection.
    """
    return [
        "FilmFanatic",
        "FoodLover",
        "Hobbyist",
        "JustForFun",
        "LifeStories",
        "OfficeCulture",
        "WouldYouRather",
    ]


def get_random_prompt_by_topic(topic: str) -> Tuple[str, str, str]:
    """
    Returns (prompt_id, prompt_text, tags) for a random prompt matching the given topic tag.
    Falls back to a fully random prompt if no match is found.
    """
    df = load_prompts_df()
    tags_col = _get_col(df, ["tags", "tag"])

    if tags_col is not None:
        mask = df[tags_col].astype(str).apply(
            lambda cell: any(t.strip().lower() == topic.lower() for t in cell.split(","))
        )
        filtered = df[mask]
    else:
        filtered = pd.DataFrame()

    if filtered.empty:
        return get_random_prompt_text()

    id_col = _get_col(filtered, ["prompt_id", "id"])
    text_col = _get_col(filtered, ["prompt_text", "text", "prompt"])

    row = filtered.sample(n=1).iloc[0].to_dict()

    if id_col and id_col != "prompt_id":
        row["prompt_id"] = row[id_col]
    if text_col and text_col != "prompt_text":
        row["prompt_text"] = row[text_col]
    if not id_col:
        row["prompt_id"] = str(filtered.sample(n=1).index[0])

    tags_val = str(row.get(tags_col, "")) if tags_col else ""
    return str(row["prompt_id"]), str(row["prompt_text"]), tags_val


def mark_prompt_asked(prompt_id: str) -> None:
    """
    Mark a prompt as 'asked' by updating a timestamp column (if present),
    and writing the CSV back to disk.
    """
    df = load_prompts_df()

    id_col = _get_col(df, ["prompt_id", "id"])
    asked_col = _get_col(df, ["asked_at", "last_asked_at", "asked", "last_asked"])

    if id_col is None:
        # If CSV doesn't have an id column, we can't reliably update a row.
        # No-op instead of crashing.
        return

    if asked_col is None:
        # If there is no asked column, also no-op (keeps behavior non-breaking).
        return

    now_str = datetime.now().isoformat(timespec="seconds")

    # Match prompt_id as string comparison to be safe
    mask = df[id_col].astype(str) == str(prompt_id)
    if mask.any():
        df.loc[mask, asked_col] = now_str
        df.to_csv(PROMPTS_CSV, index=False)