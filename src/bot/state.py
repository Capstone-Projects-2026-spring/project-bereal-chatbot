# src/bot/state.py
from dataclasses import dataclass, field
from threading import Lock
from typing import Optional, Set


@dataclass
class BotState:
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
    _reminder_delay_minutes: int = 10
    _pending_custom_prompt: Optional[str] = None  # user-authored prompt text
    _user_prompt_creator_used_today: bool = False  # only invite one user to create a prompt
    _social_connector_used_today: bool = False  # only run social connector once per day

    def set_last_prompt_ts(self, ts: Optional[str]) -> None:
        with self._lock:
            self._last_prompt_ts = ts
            self._reminder_sent = False

    def get_last_prompt_ts(self) -> Optional[str]:
        with self._lock:
            return self._last_prompt_ts

    def get_reminder_sent(self) -> bool:
        with self._lock:
            return self._reminder_sent

    def set_reminder_sent(self, value: bool) -> None:
        with self._lock:
            self._reminder_sent = value

    def get_reminder_delay_minutes(self) -> int:
        with self._lock:
            return self._reminder_delay_minutes

    def set_reminder_delay_minutes(self, value: int) -> None:
        with self._lock:
            self._reminder_delay_minutes = value

    def set_active_tags(self, tags: Set[str]) -> None:
        with self._lock:
            self._active_tags = tags

    def get_active_tags(self) -> Set[str]:
        with self._lock:
            return set(self._active_tags)

    def set_pending_topic(self, topic: Optional[str]) -> None:
        with self._lock:
            self._pending_topic = topic

    def get_and_clear_pending_topic(self) -> Optional[str]:
        """Returns the pending topic and clears it so it only applies once."""
        with self._lock:
            topic = self._pending_topic
            self._pending_topic = None
            return topic

    def set_daily_target_time(self, t: Optional[str]) -> None:
        with self._lock:
            self._daily_target_time = t

    def set_active_channel(self, channel: Optional[str]) -> None:
        with self._lock:
            self._active_channel = channel

    def get_active_channel(self) -> Optional[str]:
        with self._lock:
            return self._active_channel

    def set_active_token(self, token: Optional[str]) -> None:
        with self._lock:
            self._active_token = token

    def get_active_token(self) -> Optional[str]:
        with self._lock:
            return self._active_token

    def get_daily_target_time(self) -> Optional[str]:
        with self._lock:
            return self._daily_target_time

    def set_selected_preset(self, value: Optional[str]) -> None:
        with self._lock:
            self._selected_preset = value

    def get_selected_preset(self) -> Optional[str]:
        with self._lock:
            return self._selected_preset

    def set_selected_mode(self, value: Optional[str]) -> None:
        with self._lock:
            self._selected_mode = value

    def get_selected_mode(self) -> Optional[str]:
        with self._lock:
            return self._selected_mode

    def set_random_start_time(self, value: Optional[str]) -> None:
        with self._lock:
            self._random_start_time = value

    def get_random_start_time(self) -> Optional[str]:
        with self._lock:
            return self._random_start_time

    def set_random_end_time(self, value: Optional[str]) -> None:
        with self._lock:
            self._random_end_time = value

    def get_random_end_time(self) -> Optional[str]:
        with self._lock:
            return self._random_end_time

    def set_static_time(self, value: Optional[str]) -> None:
        with self._lock:
            self._static_time = value

    def get_static_time(self) -> Optional[str]:
        with self._lock:
            return self._static_time

    def set_active_days(self, days: Set[str]) -> None:
        with self._lock:
            self._active_days = days

    def get_active_days(self) -> Set[str]:
        with self._lock:
            return set(self._active_days)

    def is_today_active(self) -> bool:
        from datetime import date
        today = date.today().strftime("%A")  # e.g. "Monday"
        with self._lock:
            return today in self._active_days

    def set_pending_custom_prompt(self, text: Optional[str]) -> None:
        with self._lock:
            self._pending_custom_prompt = text

    def get_and_clear_pending_custom_prompt(self) -> Optional[str]:
        with self._lock:
            text = self._pending_custom_prompt
            self._pending_custom_prompt = None
            return text

    def set_user_prompt_creator_used_today(self, value: bool) -> None:
        with self._lock:
            self._user_prompt_creator_used_today = value

    def get_user_prompt_creator_used_today(self) -> bool:
        with self._lock:
            return self._user_prompt_creator_used_today

    def set_social_connector_used_today(self, value: bool) -> None:
        with self._lock:
            self._social_connector_used_today = value

    def get_social_connector_used_today(self) -> bool:
        with self._lock:
            return self._social_connector_used_today


def get_team_id(body: dict) -> Optional[str]:
    """Extract team_id from a Slack request body, handling both slash commands and block actions."""
    return body.get("team_id") or (body.get("team") or {}).get("id")


def create_state(default_channel: Optional[str] = None) -> BotState:
    state = BotState(_lock=Lock())
    if default_channel:
        state.set_active_channel(default_channel)
    return state


class StateManager:
    def __init__(self):
        self._states = {}
        self._lock = Lock()

    def get_state(self, team_id: str) -> BotState:
        with self._lock:
            if team_id not in self._states:
                self._states[team_id] = BotState(_lock=Lock())
            return self._states[team_id]

    def all_states(self) -> dict:
        with self._lock:
            return dict(self._states)
