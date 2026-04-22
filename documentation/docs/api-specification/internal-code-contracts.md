---
sidebar_position: 3
title: Internal Code Contracts
description: Class and module contract standards, including exception and error-handling policies.
---

# Internal Code Contracts

## Purpose

This page defines how internal classes and modules are documented in VibeCheck. It complements the class diagram and is intended for maintainers implementing or changing runtime logic.

---

# Implemented Contracts


## Class: PromptTracker

**Purpose**: Tracks per-workspace prompt usage metrics and response counts in MongoDB.

### Fields

| Field | Type | Visibility | Purpose | Invariants |
| --- | --- | --- | --- | --- |
| _col | Mongo collection handle | private | Stores prompt statistics documents | Bound to vibecheck.prompt_stats |
| _active_prompt | dict[(team_id, channel_id), prompt_id] | private | Maps channel/workspace to active prompt for response counting | Keys are tuple(team_id, channel), values are string prompt ids |

### Public Methods

#### __init__(mongo_uri: str) -> None

- Purpose: Initialize MongoDB connection and runtime index map.
- Preconditions: mongo_uri is valid and reachable by runtime.
- Postconditions: collection handle and active prompt map are initialized.
- Throws: PyMongo connection exceptions when connection cannot be created.
- Side-effects: opens DB client connection.
- Retry and idempotency: constructor call is not idempotent at process level.

#### record_prompt_sent(prompt_id: str, prompt_text: str, tags: str, channel: str, team_id: str) -> None

- Purpose: Upsert prompt stats and increment times_asked.
- Preconditions:
  - team_id and channel identify a workspace context.
  - prompt_id and prompt_text are non-empty for meaningful metrics.
- Postconditions:
  - Prompt document exists for (team_id, prompt_id).
  - times_asked increased by 1.
  - last_asked_at updated to current UTC time.
  - active prompt map updated for (team_id, channel).
- Throws:
  - Database exceptions on write failure.
- Side-effects: writes to MongoDB and mutates in-memory map.
- Retry and idempotency: not idempotent; retries will increment times_asked again.

#### record_response(channel: str, team_id: str) -> None

- Purpose: Increment times_responded for active prompt in channel/workspace.
- Preconditions: active prompt exists for (team_id, channel) or operation no-ops.
- Postconditions:
  - If active prompt exists, times_responded is incremented by 1.
  - If none exists, no DB mutation occurs.
- Throws:
  - Database exceptions on write failure.
- Side-effects: writes to MongoDB.
- Retry and idempotency: not idempotent; retries increment counter repeatedly.

#### get_all_stats(team_id: str) -> list[dict]

- Purpose: Return workspace prompt stats sorted by times_asked descending.
- Preconditions: team_id is provided.
- Postconditions: returns list of documents without Mongo _id field.
- Throws:
  - Database exceptions on query failure.
- Side-effects: none outside DB read.
- Retry and idempotency: idempotent read; safe to retry.

### Example Usage

```python
from services.mongo_service import PromptTracker

tracker = PromptTracker(mongo_uri)
tracker.record_prompt_sent("12", "Share your current vibe", "social", "C123", "T123")
stats = tracker.get_all_stats("T123")
```

## Class: BotState

### Purpose

Stores mutable, per-workspace runtime configuration for scheduling, channels, tags, and one-time prompt overrides.

### Fields

| Field | Type | Visibility | Purpose | Invariants |
| --- | --- | --- | --- | --- |
| _lock | threading.Lock | private | Guards all state reads/writes | Must be held when reading/writing private fields |
| _daily_target_time | Optional[str] | private | Current selected prompt time | Time format should be HH:MM:SS AM/PM when set |
| _active_channel | Optional[str] | private | Channel used for posting/listening | Slack channel identifier semantics |
| _active_token | Optional[str] | private | OAuth bot token for the workspace | Set at channel configuration time |
| _selected_preset | Optional[str] | private | Currently selected preset option key | Values of form `time_N` |
| _selected_mode | Optional[str] | private | Scheduling mode | Expected values include mode_random, mode_preset, mode_static |
| _random_start_time | Optional[str] | private | Start of random scheduling window | Time format HH:MM:SS AM/PM when set |
| _random_end_time | Optional[str] | private | End of random scheduling window | Time format HH:MM:SS AM/PM when set |
| _static_time | Optional[str] | private | Fixed time used in static mode | Time format HH:MM:SS AM/PM when set |
| _active_days | Set[str] | private | Days when posting is enabled | Members must be valid weekday names |
| _pending_topic | Optional[str] | private | One-time topic override | Cleared after retrieval |
| _active_tags | Set[str] | private | Allowed prompt tag filter | Empty set means all tags allowed |
| _last_prompt_ts | Optional[str] | private | Slack message timestamp of last posted prompt | Used to match response reactions for tracking |
| _reminder_sent | bool | private | Whether reminder DM has been sent for current prompt | Reset to False when a new prompt is posted |
| _reminder_delay_minutes | int | private | Minutes after prompt post before sending reminders | Defaults to 10 |
| _pending_custom_prompt | Optional[str] | private | User-authored prompt text pending posting | Cleared after retrieval |
| _user_prompt_creator_used_today | bool | private | Whether a user has been invited to create today's prompt | Ensures only one invite per day |
| _social_connector_used_today | bool | private | Whether the social connector has run today | Ensures it runs at most once per day |

### Public Methods (Representative)

#### set_daily_target_time(t: Optional[str]) -> None

- Purpose: Update scheduled target time.
- Preconditions: if provided, t follows expected time format.
- Postconditions: _daily_target_time updated under lock.
- Throws: no explicit exception; caller validation is expected upstream.
- Side-effects: mutates in-memory state.
- Retry and idempotency: idempotent when setting same value.

#### get_daily_target_time() -> Optional[str]

- Purpose: Return current target time.
- Preconditions: none.
- Postconditions: returns snapshot value under lock.
- Throws: none expected.
- Side-effects: none.
- Retry and idempotency: idempotent read.

#### set_active_days(days: Set[str]) -> None

- Purpose: Replace active posting days.
- Preconditions: days contains valid weekday names.
- Postconditions: _active_days replaced under lock.
- Throws: none explicit.
- Side-effects: mutates in-memory state.
- Retry and idempotency: idempotent when setting same set.

#### is_today_active() -> bool

- Purpose: Determine whether posting is enabled for current weekday.
- Preconditions: _active_days contains weekday strings.
- Postconditions: returns True if current day in active set.
- Throws: none expected.
- Side-effects: none.
- Retry and idempotency: idempotent read.

### Example Usage

```python
from bot.state import create_state

state = create_state(default_channel="#general")
state.set_selected_mode("mode_random")
state.set_daily_target_time("02:00:00 PM")
if state.is_today_active():
    print(state.get_daily_target_time())
```

## Class: StateManager

### Purpose

Creates and returns one BotState instance per workspace team id.

### Fields

| Field | Type | Visibility | Purpose | Invariants |
| --- | --- | --- | --- | --- |
| _states | dict[str, BotState] | private | Workspace state registry | Exactly one BotState per team_id key |
| _lock | threading.Lock | private | Synchronizes registry access | Must guard reads/writes of _states |

### Public Methods

#### get_state(team_id: str) -> BotState

- Purpose: Return existing state for team_id or create one if missing.
- Preconditions: team_id is non-empty for stable keying.
- Postconditions: returned BotState exists in _states.
- Throws: none explicit.
- Side-effects: may allocate and register new BotState.
- Retry and idempotency: idempotent for same team_id after first call.

#### all_states() -> dict

- Purpose: Return shallow copy of all registered states.
- Preconditions: none.
- Postconditions: caller receives copy, not direct internal map reference.
- Throws: none explicit.
- Side-effects: none.
- Retry and idempotency: idempotent read.

### Example Usage

```python
from bot.state import StateManager

manager = StateManager()
team_state = manager.get_state("T123")
team_state.set_active_channel("#general")
```

## Module: prompt_service

### Purpose

Loads prompt catalog data, selects prompts by policy, and persists asked timestamps when supported by CSV columns.

### Module Data

| Name | Type | Visibility | Purpose | Invariants |
| --- | --- | --- | --- | --- |
| _PROMPTS_DF | Optional[pandas.DataFrame] | private module-level | In-memory prompt cache | None or DataFrame with normalized columns |

### Public Functions (Representative)

#### load_prompts_df(force_reload: bool = False) -> pandas.DataFrame

- Purpose: Load and cache prompt CSV data.
- Preconditions: prompt CSV exists at configured path.
- Postconditions: returns DataFrame and updates cache.
- Throws:
  - FileNotFoundError when CSV path is missing.
  - pandas parsing exceptions on malformed CSV.
- Side-effects: reads disk, updates module cache.
- Retry and idempotency: idempotent for successful repeated reads unless force_reload.

#### get_random_prompt_text(response_type: Optional[str] = None, active_tags: Optional[set] = None) -> tuple[str, str, str]

- Purpose: Return random prompt id, text, and tags with optional filters.
- Preconditions: dataset contains at least one valid prompt text column.
- Postconditions: tuple contains normalized string values.
- Throws:
  - RuntimeError if no acceptable text column exists.
- Side-effects: may load CSV cache.
- Retry and idempotency: not idempotent (randomized selection).

#### mark_prompt_asked(prompt_id: str) -> None

- Purpose: Mark prompt as asked by writing timestamp to CSV when supported.
- Preconditions: CSV has id column and asked timestamp column.
- Postconditions:
  - Matching row timestamp updated when columns exist.
  - No-op when required columns are missing.
- Throws:
  - File I/O exceptions on write failure.
- Side-effects: writes CSV file.
- Retry and idempotency: effectively idempotent over short interval for same prompt, but timestamp value may differ.

### Example Usage

```python
from services.prompt_service import get_random_prompt_text, mark_prompt_asked

prompt_id, text, tags = get_random_prompt_text(active_tags={"social"})
mark_prompt_asked(prompt_id)
```

## Module: mongo_service (user_interests)

:::info
**Purpose**: Stores and retrieves per-user topic interest tags in MongoDB, used by the social connector and onboarding flow.
:::

### Module Data

| Name | Type | Visibility | Purpose | Invariants |
| --- | --- | --- | --- | --- |
| _mongo_client | Optional[MongoClient] | private module-level | Shared client for user_interests operations | Lazily initialized on first use if not pre-warmed |

### Public Functions (Representative)

#### init_user_interests(mongo_uri: str) -> None

- **Purpose:** Pre-warm the MongoDB connection at startup.
- Preconditions: mongo_uri is valid and reachable.
- Postconditions: `_mongo_client` is initialized and connection is verified via ping.
- Throws: PyMongo exceptions on connection failure.
- Side-effects: opens DB client, runs admin ping.
- Retry and idempotency: not idempotent; replaces existing client reference.

#### save_user_interests(team_id: str, user_id: str, tags: list[str]) -> None

- **Purpose:** Upsert interest tags for a user in the `vibecheck.user_interests` collection.
- Preconditions: team_id and user_id are non-empty.
- Postconditions: document for (team_id, user_id) exists with updated tags and `updated_at`.
- Throws: PyMongo exceptions on write failure.
- Side-effects: writes to MongoDB.
- Retry and idempotency: idempotent for same tags input.

#### get_user_interests(team_id: str, user_id: str) -> list[str]

- **Purpose:** Return stored interest tags for a user, or an empty list if none exist.
- Preconditions: none.
- Postconditions: returns list; never raises on missing document.
- Throws: PyMongo exceptions on query failure.
- Side-effects: none.
- Retry and idempotency: idempotent read.

#### get_all_user_interests(team_id: str) -> list[dict]

- **Purpose:** Return all users and their interest tags for a given workspace.
- Preconditions: team_id is non-empty.
- Postconditions: returns list of `{user_id, tags}` dicts; empty list if none exist.
- Throws: PyMongo exceptions on query failure.
- Side-effects: none.
- Retry and idempotency: idempotent read.

### Example Usage

```python
from services.mongo_service import save_user_interests, get_user_interests

save_user_interests("T123", "U456", ["social", "food"])
tags = get_user_interests("T123", "U456")  # ["social", "food"]
```

---

# Exception and Error-Handling Policy

- Database exceptions from PyMongo propagate to the caller; callers are responsible for logging and recovery.
- File I/O exceptions from prompt_service propagate to the caller.
- BotState and StateManager methods do not raise; they are safe to call without a try/except.
- All mutations that must be visible across threads must be made through state accessor methods, never by writing private fields directly.

---

# Logging and Telemetry

- PromptTracker operations are not individually logged; callers log at their level.
- BotState mutations are not logged; the control panel and scheduler log relevant state changes.
- prompt_service logs a warning if required CSV columns are missing.

---

# Retry and Idempotency Summary

| Operation | Idempotent | Notes |
| --- | --- | --- |
| record_prompt_sent | No | Increments counter on each call |
| record_response | No | Increments counter on each call |
| get_all_stats | Yes | Read-only |
| BotState setters | Yes | Same value produces same state |
| load_prompts_df | Yes | Returns cached result unless force_reload |
| get_random_prompt_text | No | Randomly selects each time |
| mark_prompt_asked | Effectively yes | Overwrites timestamp |
| save_user_interests | Yes | Upserts; same tags produce same result |
| get_user_interests | Yes | Read-only |

---

# Maintenance Rule

When adding new fields to BotState, add corresponding getter and setter methods and update this contract's Fields table.