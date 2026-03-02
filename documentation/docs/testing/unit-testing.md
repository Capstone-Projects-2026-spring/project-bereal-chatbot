---
sidebar_position: 1
---
# Unit tests

Unit tests are written using pytest for VibeCheck's core time-selection logic and Slack command handlers.

### Time Library Component

***test_preset_time_library_valid_choices(choice, expected)***

	Test: Tests whether `preSet_time_library()` maps each valid numeric option (1 through 11) to the correct scheduled time string.
	Returns: True if the returned time string matches the expected preset time for each valid input, otherwise false.

***test_preset_time_library_invalid_choices_return_none(invalid_choice)***

	Test: Tests whether `preSet_time_library()` safely handles invalid numeric inputs outside the supported range.
	Returns: True if the function returns `None` for invalid inputs (0, 12, -1, 999), otherwise false.

### Slack Command Component

***test_handle_findtime_command_ack_and_respond()***

	Test: Tests whether `/findtime` acknowledges the command and responds with the current `daily_target_time` value.
	Returns: True if `ack()` is called once and `respond()` contains the expected scheduled time string, otherwise false.

***test_pick_time_without_argument_shows_options()***

	Test: Tests whether `/picktime` returns the list of available preset times when no argument is provided.
	Returns: True if `ack()` is called once and the response contains the time options list, otherwise false.

***test_pick_time_with_valid_choice_updates_global()***

	Test: Tests whether `/picktime <number>` updates the global `daily_target_time` when the number is valid.
	Returns: True if `daily_target_time` is updated to the expected value and the success response is returned, otherwise false.

***test_pick_time_out_of_range()***

	Test: Tests whether `/picktime` rejects numbers outside the supported range (1-11).
	Returns: True if `ack()` is called and the out-of-range validation message is returned, otherwise false.

***test_pick_time_non_numeric()***

	Test: Tests whether `/picktime` rejects non-numeric input.
	Returns: True if `ack()` is called and the invalid-number validation message is returned, otherwise false.

***test_random_time_sets_new_target()***

	Test: Tests whether `/randomtime` chooses a new time and updates `daily_target_time` using a deterministic mocked random value.
	Returns: True if `ack()` is called, `daily_target_time` is updated correctly, and the success response is returned, otherwise false.

### Test Doubles and Isolation

External Slack dependencies are stubbed using mock objects (`DummyClient`, `DummyApp`, and mocked `ack/respond` callbacks) so unit tests run offline and validate only command logic.
