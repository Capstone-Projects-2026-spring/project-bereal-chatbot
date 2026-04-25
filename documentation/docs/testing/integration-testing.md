---
sidebar_position: 2
---
# Integration tests

This page tracks integration-level command and workflow coverage for the current Slack app implementation.

### Current slash command inventory

Active slash commands currently registered in the bot:

- `/setchannel`
- `/forceprompt`
- `/picktags`
- `/connect`
- `/findtime`
- `/picktime`
- `/vibestatus`
- `/promptstats`
- `/picktopic`
- `/checkvibes`
- `/mentor`
- `/streak`
- `/help`

---

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

### Use Case 2 - Setting Active Channel (`/setchannel`)

***test_setchannel_updates_state()***

	Status: Implemented (tests/test_commands.py)
	Purpose: Verifies `/setchannel` updates workspace channel state and posts confirmation.
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
	Purpose: Verifies `/setchannel` rejects missing channel input.
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

### Use Case 3 - Sending Prompt (`/forceprompt`)

***test_forceprompt_acks()***

	Status: Implemented (tests/test_commands.py)
	Purpose: Verifies `/forceprompt` acknowledges immediately.
	Input parameters:
	- Command body: `{"text":"", "channel_id":"C123"}`
	Expected results:
	- ack() called exactly once
	Uses:
	- DummyApp command registry
	- Mock callbacks and Slack client object


***test_forceprompt_posts_to_command_channel()***

	Status: Implemented (tests/test_commands.py)
	Purpose: Verifies `/forceprompt` posts to command channel when no override channel is supplied.
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
	Purpose: Verifies `/forceprompt #channel` overrides the command channel.
	Input parameters:
	- Command body: `{"text":"#general", "channel_id":"C123"}`
	Expected results:
	- chat_postMessage(...) called with channel="#general"
	Uses:
	- Patched prompt dependencies and mocked client setup

---

### Use Case 4 - Managing User Interest Tags (`/picktags`)

***test_picktags_command_opens_static_checkbox_modal()***

	Status: Implemented (tests/test_commands.py)
	Purpose: Verifies `/picktags` opens the modal with static checkbox options and pre-selected existing tags.
	Input parameters:
	- Command body with team_id, user_id, trigger_id
	- Mocked existing interest tags
	Expected results:
	- ack() called once
	- client.views_open(...) called with expected checkbox options and initial selections
	Uses:
	- DummyApp command registry
	- Patched get_user_interests


***test_picktags_submission_saves_selected_tags()***

	Status: Implemented (tests/test_commands.py)
	Purpose: Verifies modal submission persists tags and sends confirmation DM.
	Input parameters:
	- View submission payload with selected options
	Expected results:
	- save_user_interests(team_id, user_id, tags) called
	- client.chat_postMessage(...) called once
	Uses:
	- Patched save_user_interests
	- Mocked Slack client

---

### Use Case 5 - Running Social Connector (`/connect`)

***test_social_connector_finds_pair_from_shared_tags()***

	Status: Implemented (tests/test_commands.py)
	Purpose: Verifies shared-tag matching logic returns a valid pair.


***test_social_connector_randomly_selects_from_all_matching_pairs()***

	Status: Implemented (tests/test_commands.py)
	Purpose: Verifies random selection occurs from all valid matching pairs.


***test_social_connector_posts_soft_intro_message()***

	Status: Implemented (tests/test_commands.py)
	Purpose: Verifies connector posts intro plus icebreaker to the channel.


***test_social_connector_command_posts_in_current_channel()***

	Status: Implemented (tests/test_commands.py)
	Purpose: Verifies `/connect` calls connector flow for current channel/workspace.


***test_social_connector_command_responds_when_no_match_found()***

	Status: Implemented (tests/test_commands.py)
	Purpose: Verifies user gets a friendly no-match response when no eligible pair exists.

---

### Use Case 6 - Scheduler and State Integration (time behavior used by `/findtime`, `/picktime`, and App Home settings)

***test_pick_random_time_from_range()***

	Status: Implemented (tests/test_acceptance.py)
	Purpose: Verifies scheduler time selection returns a valid time within configured bounds.


***test_pick_random_time_falls_back_to_preset_when_no_range()***

	Status: Implemented (tests/test_acceptance.py)
	Purpose: Verifies fallback behavior when no explicit random range is configured.


***test_pick_random_time_after_filters_past_times()***

	Status: Implemented (tests/test_acceptance.py)
	Purpose: Verifies selected time is constrained to valid future choices for the day.


***test_full_flow_state_and_scheduler()***

	Status: Implemented (tests/test_acceptance.py)
	Purpose: Verifies state + scheduler integration preserves selected mode, selected channel, and chosen time.

---

### Use Case 7 - Viewing Prompt Statistics (`/promptstats`)

***test_promptstats_returns_sorted_summary()***

	Status: Planned
	Purpose: Verifies `/promptstats` returns formatted prompt engagement summary.
	Input parameters:
	- Mocked tracker get_all_stats() returns prompt records with ask/respond counts
	Expected results:
	- ack() called once
	- respond() includes ask/response totals in formatted output


***test_promptstats_handles_empty_data()***

	Status: Planned
	Purpose: Verifies `/promptstats` returns no-data message when stats list is empty.
	Input parameters:
	- Mocked tracker returns []
	Expected results:
	- respond() returns no-data message path

---

### Use Case 8 - Picking Topic (`/picktopic`)

***test_picktopic_lists_topics_when_no_arg()***

	Status: Planned
	Purpose: Verifies `/picktopic` (without args) lists available topics and usage hint.


***test_picktopic_sets_pending_topic_when_valid()***

	Status: Planned
	Purpose: Verifies `/picktopic <topic>` stores one-time pending topic in workspace state.


***test_picktopic_rejects_unknown_topic()***

	Status: Planned
	Purpose: Verifies `/picktopic` returns validation guidance for invalid topics.

---

### Use Case 9 - Time Commands (`/findtime` and `/picktime`)

***test_findtime_returns_target_time_and_mode()***

	Status: Planned
	Purpose: Verifies `/findtime` reports workspace target time and active mode.


***test_picktime_lists_options_when_empty()***

	Status: Planned
	Purpose: Verifies `/picktime` without argument returns preset list.


***test_picktime_sets_target_time_for_valid_choice()***

	Status: Planned
	Purpose: Verifies `/picktime <1..11>` updates state daily target time.


***test_picktime_rejects_invalid_input()***

	Status: Planned
	Purpose: Verifies `/picktime` handles non-numeric and out-of-range values safely.

---

### Use Case 10 - Viewing Status (`/vibestatus`)

***test_vibestatus_random_mode_summary()***

	Status: Planned
	Purpose: Verifies `/vibestatus` includes mode label, channel, target time, active days, and posting status for random mode.


***test_vibestatus_static_mode_summary()***

	Status: Planned
	Purpose: Verifies `/vibestatus` reports static time correctly when static mode is active.

---

### Use Case 11 - Help Command (`/help`)

***test_help_returns_setup_guide_text()***

	Status: Planned
	Purpose: Verifies `/help` returns non-empty setup and usage guidance and acknowledges once.

---

### Use Case 12 - Mentor Program Command (`/mentor`)

***test_mentor_signup_opens_modal_for_valid_role()***

	Status: Planned
	Purpose: Verifies `/mentor signup mentor|mentee` opens the signup modal when user is not already registered.


***test_mentor_status_returns_waiting_or_pairing()***

	Status: Planned
	Purpose: Verifies `/mentor status` returns correct summary for unmatched and matched users.


***test_mentor_leave_removes_registration_and_clears_pair()***

	Status: Planned
	Purpose: Verifies `/mentor leave` removes profile and clears existing pairing.


***test_mentor_match_notifies_pairs_when_available()***

	Status: Planned
	Purpose: Verifies `/mentor match` creates and notifies pairs when compatible unmatched users exist.

---

### Use Case 13 - Vibe Analytics Command (`/checkvibes`)

***test_checkvibes_defaults_to_today()***

	Status: Planned
	Purpose: Verifies `/checkvibes` with no args triggers analysis for current day.


***test_checkvibes_accepts_all_and_date_filters()***

	Status: Planned
	Purpose: Verifies `/checkvibes all`, `/checkvibes yesterday`, and `/checkvibes MM-DD-YYYY` parse correctly.


***test_checkvibes_invalid_date_returns_validation_error()***

	Status: Planned
	Purpose: Verifies invalid date input returns a user-facing validation response.

---

### Automation notes

- All automated tests are run with pytest.
- External services (Slack API, OAuth requests, MongoDB, and LLM-dependent calls) are mocked or patched in integration-style tests.
- Existing automated coverage for slash command flows is strongest today for `/forceprompt`, `/setchannel`, `/picktags`, and `/connect`; other active slash commands are now explicitly tracked as planned integration scenarios.


