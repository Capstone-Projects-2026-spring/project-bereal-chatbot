# src/bot/state.py
from dataclasses import dataclass, field
from threading import Lock
from typing import Optional, Set


@dataclass
class BotState:
    """Thread-safe per-workspace bot configuration and runtime state."""

    _lock: Lock
    _daily_target_time: Optional[str] = None
    _active_channel: Optional[str] = None
    _selected_preset: Optional[str] = None
    _selected_mode: Optional[str] = None
    _random_start_time: Optional[str] = None
    _random_end_time: Optional[str] = None
    _static_time: Optional[str] = None
    _active_days: Set[str] = field(default_factory=lambda: {
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
    })
    _active_token: Optional[str] = None
    _pending_topic: Optional[str] = None
    _active_tags: Set[str] = field(default_factory=set)  # empty = all tags allowed
    _last_prompt_ts: Optional[str] = None
    _reminder_sent: bool = False
    _reminder_enabled: bool = False
    _pending_custom_prompt: Optional[str] = None  # user-authored prompt text
    _user_prompt_creator_used_today: bool = False  # only invite one user to create a prompt
    _social_connector_used_today: bool = False  # only run social connector once per day
    _mentor_checkin_week: Optional[int] = None  # ISO week number of last mentor check-in sent
    _prompt_response_type: str = "image"  # "image", "text", or "any"
    _last_prompt_channel: Optional[str] = None  # channel where the last prompt was posted

    def set_last_prompt_ts(self, ts: Optional[str], channel: Optional[str] = None) -> None:
        """Store the timestamp of the last prompt and reset the reminder flag."""
        with self._lock:
            self._last_prompt_ts = ts
            self._reminder_sent = False
            if channel:
                self._last_prompt_channel = channel

    def get_last_prompt_ts(self) -> Optional[str]:
        """Return the Slack message timestamp of the last posted prompt."""
        with self._lock:
            return self._last_prompt_ts

    def get_reminder_sent(self) -> bool:
        """Return whether a reminder has already been sent for the current prompt."""
        with self._lock:
            return self._reminder_sent

    def set_reminder_sent(self, value: bool) -> None:
        """Mark whether a reminder has been sent for the current prompt."""
        with self._lock:
            self._reminder_sent = value

    def get_reminder_enabled(self) -> bool:
        """Return whether prompt reminders are enabled for this workspace."""
        with self._lock:
            return self._reminder_enabled

    def set_reminder_enabled(self, value: bool) -> None:
        """Enable or disable prompt reminders for this workspace."""
        with self._lock:
            self._reminder_enabled = value

    def set_active_tags(self, tags: Set[str]) -> None:
        """Replace the set of tags used to filter prompt selection."""
        with self._lock:
            self._active_tags = tags

    def get_active_tags(self) -> Set[str]:
        """Return a snapshot of the active tag filter set."""
        with self._lock:
            return set(self._active_tags)

    def set_pending_topic(self, topic: Optional[str]) -> None:
        """Queue a topic to be used as context for the next prompt."""
        with self._lock:
            self._pending_topic = topic

    def get_and_clear_pending_topic(self) -> Optional[str]:
        """Returns the pending topic and clears it so it only applies once."""
        with self._lock:
            topic = self._pending_topic
            self._pending_topic = None
            return topic

    def set_daily_target_time(self, t: Optional[str]) -> None:
        """Set the resolved daily target time (HH:MM) for the current day."""
        with self._lock:
            self._daily_target_time = t

    def set_active_channel(self, channel: Optional[str]) -> None:
        """Set the Slack channel ID where prompts will be posted."""
        with self._lock:
            self._active_channel = channel

    def get_active_channel(self) -> Optional[str]:
        """Return the Slack channel ID where prompts will be posted."""
        with self._lock:
            return self._active_channel

    def set_active_token(self, token: Optional[str]) -> None:
        """Store the Slack bot token for this workspace."""
        with self._lock:
            self._active_token = token

    def get_active_token(self) -> Optional[str]:
        """Return the Slack bot token for this workspace."""
        with self._lock:
            return self._active_token

    def get_daily_target_time(self) -> Optional[str]:
        """Return the resolved daily target time (HH:MM) for the current day."""
        with self._lock:
            return self._daily_target_time

    def set_selected_preset(self, value: Optional[str]) -> None:
        """Set the active scheduling preset name."""
        with self._lock:
            self._selected_preset = value

    def get_selected_preset(self) -> Optional[str]:
        """Return the active scheduling preset name."""
        with self._lock:
            return self._selected_preset

    def set_selected_mode(self, value: Optional[str]) -> None:
        """Set the scheduling mode (e.g. 'random', 'static')."""
        with self._lock:
            self._selected_mode = value

    def get_selected_mode(self) -> Optional[str]:
        """Return the scheduling mode (e.g. 'random', 'static')."""
        with self._lock:
            return self._selected_mode

    def set_random_start_time(self, value: Optional[str]) -> None:
        """Set the earliest time (HH:MM) for random prompt scheduling."""
        with self._lock:
            self._random_start_time = value

    def get_random_start_time(self) -> Optional[str]:
        """Return the earliest time (HH:MM) for random prompt scheduling."""
        with self._lock:
            return self._random_start_time

    def set_random_end_time(self, value: Optional[str]) -> None:
        """Set the latest time (HH:MM) for random prompt scheduling."""
        with self._lock:
            self._random_end_time = value

    def get_random_end_time(self) -> Optional[str]:
        """Return the latest time (HH:MM) for random prompt scheduling."""
        with self._lock:
            return self._random_end_time

    def set_static_time(self, value: Optional[str]) -> None:
        """Set the fixed daily time (HH:MM) used in static scheduling mode."""
        with self._lock:
            self._static_time = value

    def get_static_time(self) -> Optional[str]:
        """Return the fixed daily time (HH:MM) used in static scheduling mode."""
        with self._lock:
            return self._static_time

    def set_active_days(self, days: Set[str]) -> None:
        """Replace the set of weekday names on which prompts are posted."""
        with self._lock:
            self._active_days = days

    def get_active_days(self) -> Set[str]:
        """Return a snapshot of the weekday names on which prompts are posted."""
        with self._lock:
            return set(self._active_days)

    def is_today_active(self) -> bool:
        """Return True if today's weekday is in the active days set."""
        from datetime import date
        today = date.today().strftime("%A")  # e.g. "Monday"
        with self._lock:
            return today in self._active_days

    def set_pending_custom_prompt(self, text: Optional[str]) -> None:
        """Queue a user-authored prompt text to be used instead of a generated one."""
        with self._lock:
            self._pending_custom_prompt = text

    def get_and_clear_pending_custom_prompt(self) -> Optional[str]:
        """Return the pending custom prompt text and clear it so it is used only once."""
        with self._lock:
            text = self._pending_custom_prompt
            self._pending_custom_prompt = None
            return text

    def set_user_prompt_creator_used_today(self, value: bool) -> None:
        """Mark whether a user has already been invited to create a prompt today."""
        with self._lock:
            self._user_prompt_creator_used_today = value

    def get_user_prompt_creator_used_today(self) -> bool:
        """Return whether a user has already been invited to create a prompt today."""
        with self._lock:
            return self._user_prompt_creator_used_today

    def set_social_connector_used_today(self, value: bool) -> None:
        """Mark whether the social connector flow has already run today."""
        with self._lock:
            self._social_connector_used_today = value

    def get_social_connector_used_today(self) -> bool:
        """Return whether the social connector flow has already run today."""
        with self._lock:
            return self._social_connector_used_today

    def set_mentor_checkin_week(self, week: Optional[int]) -> None:
        """Store the ISO week number when the last mentor check-in was sent."""
        with self._lock:
            self._mentor_checkin_week = week

    def get_mentor_checkin_week(self) -> Optional[int]:
        """Return the ISO week number when the last mentor check-in was sent."""
        with self._lock:
            return self._mentor_checkin_week

    def set_prompt_response_type(self, value: str) -> None:
        """Set the expected response type for prompts: 'image', 'text', or 'any'."""
        with self._lock:
            self._prompt_response_type = value

    def get_prompt_response_type(self) -> str:
        """Return the expected response type for prompts: 'image', 'text', or 'any'."""
        with self._lock:
            return self._prompt_response_type

    def set_last_prompt_channel(self, channel: Optional[str]) -> None:
        """Set the channel ID where the most recent prompt was posted."""
        with self._lock:
            self._last_prompt_channel = channel

    def get_last_prompt_channel(self) -> Optional[str]:
        """Return the channel ID where the most recent prompt was posted."""
        with self._lock:
            return self._last_prompt_channel


def get_team_id(body: dict) -> Optional[str]:
    """Extract team_id from a Slack request body, handling both slash commands and block actions."""
    return body.get("team_id") or (body.get("team") or {}).get("id")


def create_state(default_channel: Optional[str] = None) -> BotState:
    """Create a new BotState with a fresh lock, optionally pre-setting the active channel."""
    state = BotState(_lock=Lock())
    if default_channel:
        state.set_active_channel(default_channel)
    return state


class StateManager:
    """Registry that maps workspace team IDs to their BotState instances."""

    def __init__(self):
        self._states = {}
        self._lock = Lock()

    def get_state(self, team_id: str) -> BotState:
        """Return the BotState for the given team, creating one if it does not exist."""
        with self._lock:
            if team_id not in self._states:
                self._states[team_id] = BotState(_lock=Lock())
            return self._states[team_id]

    def all_states(self) -> dict:
        """Return a shallow copy of the team_id → BotState mapping."""
        with self._lock:
            return dict(self._states)
