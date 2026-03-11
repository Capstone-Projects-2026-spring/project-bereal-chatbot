---
sidebar_position: 2
---
# Integration tests

Integration Testing is used to test use cases and sequence diagrams. We currently have 1 implemented integration use case test.


***test_integration_randomtime_then_findtime (Use case #1):***

	Test: Tests whether a VibeCheck user can trigger random daily prompt time selection and then retrieve the same selected time through `/findtime`, validating cross-command state consistency.
	Returns: True if random time is set successfully, shared state is updated, and `/findtime` returns the exact same expected prompt time; otherwise returns false.


	Uses:
	Slack command component: `random_time`, `handle_findtime_command`
	Time library component: `preSet_time_library` (via `random_time`)
	Mocked Slack API client/app: `DummyClient`, `DummyApp`
