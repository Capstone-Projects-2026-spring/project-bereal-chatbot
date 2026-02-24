# pGrab.py
import os
import random
import pandas as pd


CSV_PATH = os.path.join(os.path.dirname(__file__), "vibecheck_prompts.csv")


def _read_csv_safely(path: str) -> pd.DataFrame:
    """
    Your CSV appears to have a first line like:
        vibecheck_prompts
    before the real header row.

    This function detects that and skips the first row if needed.
    """
    with open(path, "r", encoding="utf-8") as f:
        first_line = f.readline().strip()

    # If the first line isn't a normal CSV header (no commas), skip it.
    if "," not in first_line:
        df = pd.read_csv(path, skiprows=1)
    else:
        df = pd.read_csv(path)

    # Normalize expected columns
    required = {"prompt_id", "prompt", "response_type", "tags", "times_asked", "times_responded"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")

    # Ensure numeric columns are ints (in case they load as strings)
    df["times_asked"] = pd.to_numeric(df["times_asked"], errors="coerce").fillna(0).astype(int)
    df["times_responded"] = pd.to_numeric(df["times_responded"], errors="coerce").fillna(0).astype(int)

    return df


def load_prompts_df() -> pd.DataFrame:
    """Load the prompts CSV into a DataFrame."""
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"Could not find CSV at: {CSV_PATH}")
    return _read_csv_safely(CSV_PATH)


def save_prompts_df(df: pd.DataFrame) -> None:
    """Save the prompts DataFrame back to CSV."""
    df.to_csv(CSV_PATH, index=False)


def get_random_prompt(response_type: str | None = None) -> dict:
    """
    Return a random prompt row as a dict.
    Optionally filter by response_type ('text' or 'image').
    """
    df = load_prompts_df()

    if response_type:
        df = df[df["response_type"].astype(str).str.lower() == response_type.lower()]

    if df.empty:
        raise ValueError("No prompts available with the requested filter.")

    row = df.sample(n=1).iloc[0]
    return row.to_dict()


def mark_prompt_asked(prompt_id: int) -> None:
    """Increment times_asked for the given prompt_id."""
    df = load_prompts_df()
    mask = df["prompt_id"] == int(prompt_id)
    if not mask.any():
        raise ValueError(f"prompt_id not found: {prompt_id}")

    df.loc[mask, "times_asked"] = df.loc[mask, "times_asked"] + 1
    save_prompts_df(df)


def get_random_prompt_text(response_type: str | None = None) -> tuple[int, str]:
    """
    Convenience: returns (prompt_id, prompt_text)
    """
    row = get_random_prompt(response_type=response_type)
    return int(row["prompt_id"]), str(row["prompt"])