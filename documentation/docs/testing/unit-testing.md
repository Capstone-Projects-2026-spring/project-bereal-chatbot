---
sidebar_position: 1
---
# Unit tests

Unit tests are written using pytest for VibeCheck's core logic, command handlers, and state/config behavior.

---

### Time Library Component

***test_preset_time_library_valid_choices(choice, expected)***

	Method under test: `preSet_time_library(choice)`
	Test: Valid preset index maps to the correct time string.
	Test cases:
	- Input: `choice=1` | Expected: `"09:30:00 AM"`
	- Input: `choice=10` | Expected: `"10:15:00 AM"`
	- Input: `choice=17` | Expected: `"10:50:00 AM"`
	- Input range covered: `1..17` | Expected: each index returns its mapped preset value.

***test_preset_time_library_invalid_choices_return_none(invalid_choice)***

	Method under test: `preSet_time_library(choice)`
	Test: Invalid preset index safely returns `None`.
	Test cases:
	- Input: `choice=0` | Expected: `None`
	- Input: `choice=18` | Expected: `None`
	- Input: `choice=-1` | Expected: `None`
	- Input: `choice=999` | Expected: `None`

---

### Slack Command Component

Unit-level command handler coverage in this suite currently targets `/forceprompt` and `/setchannel`.

***test_forceprompt_acks()***

	Method under test: `/forceprompt` command handler
	Test: Command acknowledges request.
	Test case:
	- Input: body `{"text":"", "channel_id":"C123"}` with mocked prompt + mocked Slack client.
	- Expected: `ack()` called exactly once.

***test_forceprompt_posts_to_command_channel()***

	Method under test: `/forceprompt` command handler
	Test: Posts prompt to command channel when no override channel is supplied.
	Test case:
	- Input: body `{"text":"", "channel_id":"C123"}`.
	- Expected: `client.chat_postMessage(...)` called with `channel="C123"`.

***test_forceprompt_posts_to_specified_channel()***

	Method under test: `/forceprompt` command handler
	Test: Posts prompt to user-specified channel.
	Test case:
	- Input: body `{"text":"#general", "channel_id":"C123"}`.
	- Expected: `client.chat_postMessage(...)` uses `channel="#general"`.

***test_setchannel_updates_state()***

	Method under test: `/setchannel` command handler
	Test: Updates workspace active channel when valid channel is provided.
	Test case:
	- Input: body `{"text":"#new-channel", "team_id":"T123"}`.
	- Expected: `ack()` called once and `state_manager.get_state("T123").get_active_channel()` equals `"#new-channel"`.

***test_setchannel_rejects_missing_channel()***

	Method under test: `/setchannel` command handler
	Test: Rejects empty channel input and responds with validation message.
	Test case:
	- Input: body `{"text":"", "team_id":"T123"}`.
	- Expected: `ack()` called once, `respond()` called once, and active channel is not updated to `"#new-channel"`.

---

### State Component

***test_state_default_channel()***

	Method under test: `create_state(default_channel)` and `get_active_channel()`
	Test case:
	- Input: `default_channel="#general"`
	- Expected: active channel is `"#general"`.

***test_state_set_and_get_active_channel()***

	Method under test: `set_active_channel()` and `get_active_channel()`
	Test case:
	- Input: set `"#announcements"`
	- Expected: returned channel is `"#announcements"`.

***test_state_set_and_get_mode()***

	Method under test: `set_selected_mode()` and `get_selected_mode()`
	Test case:
	- Input: set `"mode_random"`
	- Expected: returned mode is `"mode_random"`.

***test_state_set_and_get_static_time()***

	Method under test: `set_static_time()` and `get_static_time()`
	Test case:
	- Input: set `"02:00:00 PM"`
	- Expected: returned static time is `"02:00:00 PM"`.

***test_state_active_days_default_all_days()***

	Method under test: `get_active_days()`
	Test case:
	- Input: default state
	- Expected: contains all seven weekday names.

***test_state_set_active_days()***

	Method under test: `set_active_days()` and `get_active_days()`
	Test case:
	- Input: `{"Monday", "Wednesday", "Friday"}`
	- Expected: returned set matches exactly.

***test_state_is_today_active()***

	Method under test: `is_today_active()`
	Test case:
	- Input: default state (all days active)
	- Expected: returns `True`.

***test_state_is_today_inactive_when_days_cleared()***

	Method under test: `is_today_active()`
	Test case:
	- Input: `set_active_days(set())`
	- Expected: returns `False`.

---

### Configuration Component

***test_required_env_var_is_set(var, monkeypatch)***

	Method under test: environment variable availability checks
	Test cases:
	- Input: each required variable set to `"dummy-value"`
	- Expected: `os.getenv(var)` is not `None` for each required variable.

***test_slack_bot_token_format(monkeypatch)***

	Method under test: Slack bot token format validation helper behavior
	Test case:
	- Input: `SLACK_BOT_TOKEN="xoxb-test-token"`
	- Expected: token starts with `"xoxb-"`.

***test_slack_app_token_format(monkeypatch)***

	Method under test: Slack app token format validation helper behavior
	Test case:
	- Input: `SLACK_APP_TOKEN="xapp-test-token"`
	- Expected: token starts with `"xapp-"`.

---

### Test Doubles and Isolation

All external classes are stubbed or mocked so unit tests run offline and isolate method behavior.

- Slack command registration is isolated with `DummyApp` (stub command registry).
- Slack API calls are isolated with mocked `client` objects and mocked callbacks (`ack`, `respond`).
- Prompt retrieval/write side effects are isolated with `patch(...)` on `get_random_prompt_text` and `mark_prompt_asked`.
- Environment-dependent behavior is isolated with `monkeypatch` for environment variables.
