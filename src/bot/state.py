# src/bot/state.py
from dataclasses import dataclass
from threading import Lock
from typing import Optional


@dataclass
class BotState:
    _lock: Lock
    _daily_target_time: Optional[str] = None
    _active_channel: Optional[str] = None

    def set_daily_target_time(self, t: Optional[str]) -> None:
        with self._lock:
            self._daily_target_time = t

    def set_active_channel(self, channel: Optional[str]) -> None:
        with self._lock:
            self._active_channel = channel

    def get_active_channel(self) -> Optional[str]:
        with self._lock:
            return self._active_channel

    def get_daily_target_time(self) -> Optional[str]:
        with self._lock:
            return self._daily_target_time


def create_state(default_channel: Optional[str] = None) -> BotState:
    state = BotState(_lock=Lock())
    if default_channel:
        state.set_active_channel(default_channel)
    return state