import pytest
from services.time_library import preSet_time_library


@pytest.mark.parametrize("choice, expected", [
    (1,  "09:30:00 AM"),
    (2,  "09:35:00 AM"),
    (3,  "09:40:00 AM"),
    (4,  "09:45:00 AM"),
    (5,  "09:50:00 AM"),
    (6,  "09:55:00 AM"),
    (7,  "10:00:00 AM"),
    (8,  "10:05:00 AM"),
    (9,  "10:10:00 AM"),
    (10, "10:15:00 AM"),
    (11, "10:20:00 AM"),
    (12, "10:25:00 AM"),
    (13, "10:30:00 AM"),
    (14, "10:35:00 AM"),
    (15, "10:40:00 AM"),
    (16, "10:45:00 AM"),
    (17, "10:50:00 AM"),
])
def test_preset_time_library_valid_choices(choice, expected):
    assert preSet_time_library(choice) == expected


@pytest.mark.parametrize("invalid_choice", [0, 18, -1, 999])
def test_preset_time_library_invalid_choices_return_none(invalid_choice):
    assert preSet_time_library(invalid_choice) is None
