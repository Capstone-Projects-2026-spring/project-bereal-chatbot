# src/bot/state.py
from dataclasses import dataclass
from threading import Lock
from typing import Optional


@dataclass
class BotState:
    _lock: Lock
    _daily_target_time: Optional[str] = None

    def set_daily_target_time(self, t: Optional[str]) -> None:
        with self._lock:
            self._daily_target_time = t

    def get_daily_target_time(self) -> Optional[str]:
        with self._lock:
            return self._daily_target_time


def create_state() -> BotState:
    return BotState(_lock=Lock())