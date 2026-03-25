import pytest
from unittest.mock import patch
from datetime import datetime
from bot.scheduler import _pick_random_time
from bot.state import create_state


@pytest.mark.acceptance
def test_pick_random_time_from_range():
    result = _pick_random_time(start_str="09:30:00 AM", end_str="10:50:00 AM")
    assert result is not None
    parsed = datetime.strptime(result, "%I:%M:%S %p")
    assert datetime.strptime("09:30:00 AM", "%I:%M:%S %p") <= parsed <= datetime.strptime("10:50:00 AM", "%I:%M:%S %p")


@pytest.mark.acceptance
def test_pick_random_time_falls_back_to_preset_when_no_range():
    result = _pick_random_time()
    assert result is not None
    datetime.strptime(result, "%I:%M:%S %p")  # valid time format


@pytest.mark.acceptance
def test_pick_random_time_after_filters_past_times():
    # Ask for a time after 10:49 AM — only 10:50 AM is valid in the preset library
    after = datetime.strptime("10:49:00 AM", "%I:%M:%S %p").replace(
        year=datetime.now().year, month=datetime.now().month, day=datetime.now().day
    )
    result = _pick_random_time(after=after)
    assert result is not None


@pytest.mark.acceptance
def test_full_flow_state_and_scheduler():
    state = create_state(default_channel="#general")
    state.set_selected_mode("mode_random")

    time = _pick_random_time(start_str="09:30:00 AM", end_str="10:50:00 AM")
    state.set_daily_target_time(time)

    assert state.get_daily_target_time() == time
    assert state.get_selected_mode() == "mode_random"
    assert state.get_active_channel() == "#general"
