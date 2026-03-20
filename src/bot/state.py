# src/bot/state.py
from dataclasses import dataclass
from threading import Lock
from typing import Optional


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


def create_state(default_channel: Optional[str] = None) -> BotState:
    state = BotState(_lock=Lock())
    if default_channel:
        state.set_active_channel(default_channel)
    return state
