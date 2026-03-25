import pytest
from bot.state import create_state


def test_state_default_channel():
    state = create_state(default_channel="#general")
    assert state.get_active_channel() == "#general"


def test_state_set_and_get_active_channel():
    state = create_state()
    state.set_active_channel("#announcements")
    assert state.get_active_channel() == "#announcements"


def test_state_set_and_get_mode():
    state = create_state()
    state.set_selected_mode("mode_random")
    assert state.get_selected_mode() == "mode_random"


def test_state_set_and_get_static_time():
    state = create_state()
    state.set_static_time("02:00:00 PM")
    assert state.get_static_time() == "02:00:00 PM"


def test_state_active_days_default_all_days():
    state = create_state()
    days = state.get_active_days()
    assert "Monday" in days
    assert "Saturday" in days
    assert len(days) == 7


def test_state_set_active_days():
    state = create_state()
    state.set_active_days({"Monday", "Wednesday", "Friday"})
    assert state.get_active_days() == {"Monday", "Wednesday", "Friday"}


def test_state_is_today_active():
    state = create_state()
    # All days active by default so today should always be active
    assert state.is_today_active() is True


def test_state_is_today_inactive_when_days_cleared():
    state = create_state()
    state.set_active_days(set())
    assert state.is_today_active() is False
