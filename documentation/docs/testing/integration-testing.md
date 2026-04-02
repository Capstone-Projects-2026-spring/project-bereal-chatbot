---
sidebar_position: 2
---
# Integration tests

### Use Case 1 - Installing VibeCheck in a Slack Workspace

***test_install_workspace_success()***

	Status: Planned

	Purpose: Verifies OAuth install flow persists installation data and returns success.

	Input parameters:
	- Mocked request query string containing a valid authorization code
	- Mocked Slack OAuth response with team.id, team.name, and access_token
	Expected results:
	- installations.update_one(...) called once with upsert=True
	- Stored record includes team_id, team_name, and bot_token
	- Success response returned from OAuth callback handler
	Uses:
	- Mocked requests.post for Slack OAuth exchange
	- Mocked MongoDB installations collection
	- Mocked Flask request context


***test_install_workspace_missing_code_returns_400()***

	Status: Planned
	Purpose: Verifies installation request fails fast when OAuth code is missing.
	Input parameters:
	- Request payload without code
	Expected results:
	- HTTP 400 response is returned
	- No installation write is attempted
	Uses:
	- Mocked Flask request context
	- Mocked MongoDB installations collection

---

### Use Case 2 - Setting Active Channel

***test_setchannel_updates_state()***

	Status: Implemented (tests/test_commands.py)
	Purpose: Verifies /setchannel updates workspace channel state and posts confirmation.
	Input parameters:
	- Command body: `{"text":"#new-channel", "team_id":"T123"}`
	- Mocked callbacks: ack, respond
	- Mocked Slack client
	Expected results:
	- ack() called exactly once
	- Workspace active channel is updated to #new-channel
	- client.chat_postMessage(...) called for channel confirmation
	Uses:
	- DummyApp command registry
	- Mock callbacks and Slack client object


***test_setchannel_rejects_missing_channel()***

	Status: Implemented (tests/test_commands.py)
	Purpose: Verifies /setchannel rejects missing channel input.
	Input parameters:
	- Command body: `{"text":"", "team_id":"T123"}`
	- Mocked callbacks: ack, respond
	Expected results:
	- ack() called once
	- Validation response is returned through respond()
	- Active channel remains unchanged
	Uses:
	- DummyApp command registry
	- Mock callbacks and Slack client object

---

### Use Case 3 - Configuring Prompt Time

***test_pick_random_time_from_range()***

	Status: Implemented (tests/test_acceptance.py)
	Purpose: Verifies scheduler time selection returns a valid time within configured bounds.
	Input parameters:
	- start_str="09:30:00 AM"
	- end_str="10:50:00 AM"
	Expected results:
	- Returned time is not None
	- Parsed time is within start/end range
	Uses:
	- Scheduler component: _pick_random_time(...)


***test_full_flow_state_and_scheduler()***

	Status: Implemented (tests/test_acceptance.py)
	Purpose: Verifies state + scheduler integration preserves selected mode, selected channel, and chosen time.
	Input parameters:
	- State created with default_channel="#general"
	- Mode set to mode_random
	- Time generated from _pick_random_time(...)
	Expected results:
	- get_daily_target_time() matches selected time
	- get_selected_mode() returns mode_random
	- get_active_channel() returns #general
	Uses:
	- Bot state component: create_state
	- Scheduler component: _pick_random_time

---

### Use Case 4 - Sending Prompt

***test_forceprompt_posts_to_command_channel()***

	Status: Implemented (tests/test_commands.py)
	Purpose: Verifies /forceprompt posts to command channel when no override channel is supplied.
	Input parameters:
	- Command body: `{"text":"", "channel_id":"C123"}`
	- Patched prompt lookup returning (prompt_id, prompt_text, tags)
	- Mocked Slack client
	Expected results:
	- ack() called once
	- chat_postMessage(...) called with channel="C123"
	- mark_prompt_asked(...) is invoked
	Uses:
	- patch("commands.force_prompt_command.get_random_prompt_text", ...)
	- patch("commands.force_prompt_command.mark_prompt_asked")
	- Mock callbacks and Slack client object


***test_forceprompt_posts_to_specified_channel()***

	Status: Implemented (tests/test_commands.py)
	Purpose: Verifies /forceprompt #channel overrides the command channel.
	Input parameters:
	- Command body: `{"text":"#general", "channel_id":"C123"}`
	- Same patched prompt dependencies as above
	Expected results:
	- chat_postMessage(...) called with channel="#general"
	Uses:
	- Same patched prompt dependencies and mocked client setup

---

### Use Case 5 - Viewing Prompt Statistics

***test_promptstats_returns_sorted_summary()***

	Status: Planned
	Purpose: Verifies /promptstats returns formatted prompt engagement summary.
	Input parameters:
	- Mocked tracker get_all_stats() returns prompt records with ask/respond counts
	- Mocked callbacks: ack, respond
	Expected results:
	- ack() called once
	- respond() includes ask/response totals in formatted output
	Uses:
	- Patch get_tracker() to return mocked tracker
	- Mock callbacks


***test_promptstats_handles_empty_data()***

	Status: Planned
	Purpose: Verifies /promptstats returns no-data message when stats list is empty.
	Input parameters:
	- Mocked tracker returns []
	Expected results:
	- respond() returns no-data message path
	Uses:
	- Patch get_tracker() and mock callbacks

---

### Automation Notes

- All integration tests are run with pytest.
- External services (Slack API, OAuth requests, and database operations) are mocked or patched.
- Test outcomes are assertion-based and pass/fail automatically.


