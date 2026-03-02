import pytest

from preSet_timeLibrary import preSet_time_library


@pytest.mark.parametrize(
    "choice, expected",
    [
        (1, "12:00:00 PM"),
        (2, "12:30:00 PM"),
        (3, "01:00:00 PM"),
        (4, "01:30:00 PM"),
        (5, "02:00:00 PM"),
        (6, "02:30:00 PM"),
        (7, "03:00:00 PM"),
        (8, "03:30:00 PM"),
        (9, "04:00:00 PM"),
        (10, "04:30:00 PM"),
        (11, "05:00:00 PM"),
    ],
)
def test_preset_time_library_valid_choices(choice, expected):
    assert preSet_time_library(choice) == expected


@pytest.mark.parametrize("invalid_choice", [0, 12, -1, 999])
def test_preset_time_library_invalid_choices_return_none(invalid_choice):
    assert preSet_time_library(invalid_choice) is None
