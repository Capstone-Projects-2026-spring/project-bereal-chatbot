---
sidebar_position: 1
title: Frontend API 
---

Frontend API - Design Document - Part II API
=============================

## Purpose

This page documents inputs users send from Slack and the outputs the bot returns through Slack responses, channel posts, and App Home interactions.

---

## Frontend Surface

VibeCheck currently exposes these user-facing interfaces in Slack:

1. Slash commands
2. App Home control panel actions
3. Bot-posted prompt messages
4. Direct-message feedback after App Home updates

---

## Slash Command Contract

| Command | Input | Output | Notes |
| --- | --- | --- | --- |
| `/findtime` | No arguments | Scheduled prompt time for the current workspace | Read-only command |
| `/picktime` | `/picktime <number>` | Confirmation or validation error | `number` must be in the supported preset range |
| `/setchannel` | `/setchannel #channel-name` | Confirmation in command response and in target channel | Updates active channel |
| `/forceprompt` | `/forceprompt [text\|image] [#channel-name]` | Confirmation or error | Can filter prompt type and optionally override channel |
| `/vibestatus` | No arguments | Current scheduling mode, channel, time, and active days | Read-only status summary |
| `/promptstats` | No arguments | Top prompt metrics for the current workspace | Read-only metrics summary |
| `/picktopic` | `/picktopic [topic]` | Topic list or confirmation | One-time override for next scheduled prompt |
| `/picktags` | No arguments | Opens interest tag modal | Stores personal topic preferences per user |
| `/help` | No arguments | Setup and usage guide | Read-only informational response |

---

## Slash Command I/O

### `/findtime`

**Request**

```text
/findtime
```

**Response**

```text
Scheduled prompt time: *02:00:00 PM* (mode: `mode_random`)
```

**Output fields**

- `scheduled prompt time`: the time currently selected for today's post
- `mode`: the saved scheduling mode for the workspace

### `/picktime`

**Request**

```text
/picktime 5
```

**Success response**

```text
Time set to: 09:50:00 AM
```

**Validation responses**

```text
Please provide a valid number between 1 and 11 to set the time
```

```text
Must pick a number between 1 and 11 to set the time.
```

**Input rules**

- `number` is required to change the stored preset time
- when omitted, the bot returns the list of available preset options

### `/setchannel`

**Request**

```text
/setchannel #general
```

**Slash command response**

```text
Active channel set to #general
```

**Channel post**

```text
The bot will now listen to this channel
```

**Validation responses**

```text
Please provide a channel name using /setchannel #channel-name
```

```text
Please provide a valid channel name starting with #
```

**Input rules**

- `#channel-name` is required; omitting it returns a validation error
- the argument must start with `#`

### `/forceprompt`

**Valid request forms**

```text
/forceprompt
/forceprompt text
/forceprompt image
/forceprompt #general
/forceprompt text #general
```

**Success response**

```text
✅ Posted a prompt to #general.
```

**Error response**

```text
❌ Failed to post prompt: <exception message>
```

**Output behavior**

- posts a prompt message into the resolved Slack channel
- records prompt metrics when the tracker is enabled
- optionally filters by `text` or `image`

**Input rules**

- all arguments are optional
- `text` or `image` filters the prompt type; omitting it selects from all types
- `#channel-name` overrides the target channel; omitting it uses the channel where the command was invoked
- arguments can appear in any order

### `/vibestatus`

**Request**

```text
/vibestatus
```

**Response**

```text
*Vibe Check Bot Status*
• *Mode:* Random (09:00:00 AM – 05:00:00 PM)
• *Channel:* #general
• *Today's prompt time:* 02:00:00 PM
• *Active days:* Monday, Wednesday, Friday
• *Posting today:* yes
```

**Output fields**

- mode
- active channel
- today's resolved prompt time
- active days
- whether the bot will post today

### `/promptstats`

**Request**

```text
/promptstats
```

**Response**

```text
*Prompt Stats (most asked first)*
• [asked 8x | responses 5] _work_life_ — What are you doing after class today?…
• [asked 6x | responses 2] _friends, social_ — Show your current vibe in one picture…
```

**Output fields**

- `times asked`
- `responses`
- prompt tags
- truncated prompt text

### `/picktopic`

**Request (no args — list available topics)**

```text
/picktopic
```

**Response**

```text
*Available topics:*
  • `food`
  • `social`
  • `work_life`

Usage: `/picktopic <topic>` — the next scheduled prompt will use that topic.
```

**Request (set topic)**

```text
/picktopic social
```

**Success response**

```text
Topic set, the next prompt will be from the `social` topic.
```

**Validation response**

```text
Unknown topic `xyz`. Pick from the available topics: `food`, `social`, `work_life`
```

**Input rules**

- when no argument is provided, returns the topic list
- the override applies to the next scheduled prompt only and resets after it fires

### `/picktags`

**Request**

```text
/picktags
```

**Response**

Opens a modal with a checkbox list of available topic tags. The user selects their interests and submits. Tags are stored per-user in MongoDB and have no effect on which prompts the bot sends.

**Output behavior**

- opens `user_interests_modal`
- on submit, saves selected tags via `save_user_interests`
- on skip, closes the modal without saving

### `/help`

**Request**

```text
/help
```

**Response**

```text
*Vibe Check Bot — Setup & Usage Guide*

*Step 1: Add the bot to your channel*
...
```

Returns the full setup and usage guide as a Slack response, including configuration steps, available commands, and descriptions of the user-created prompt and social connector features.

---

## App Home Control Panel I/O

The App Home tab is an interactive frontend surface backed by Slack Block Kit actions.

| Action ID | Input | Output | Stored Effect |
| --- | --- | --- | --- |
| `mode_selection` | selected radio button | DM confirmation message | updates scheduling mode |
| `start_time` | free-text time in `HH:MM:SS AM/PM` | validation feedback or updated view | updates random range start |
| `end_time` | free-text time in `HH:MM:SS AM/PM` | validation feedback or updated view | updates random range end |
| `preset_time_selection` | selected preset time | updated App Home state | updates preset time |
| `static_entry` | free-text time in `HH:MM:SS AM/PM` | validation feedback or updated view | updates static time |
| `active_days_selection` | selected weekdays | updated App Home state | updates active posting days |
| `tag_filter_selection` | selected topic tags | updated App Home state | updates allowed prompt tags |
| `topic_selection` | one-time topic override | updated App Home state | sets next prompt override |
| `reminder_delay_selection` | selected delay in minutes | DM confirmation | updates DM reminder delay |
| `admin_assign_prompt_creator` | selected user | DM confirmation | sends prompt creation invite to selected user |

### Example App Home feedback

```text
:gear: *Operation mode* changed to `mode_random`
:clock1: *Preset time* set to `09:30:00 AM`
:calendar: *Active days* set to: Friday, Monday, Wednesday
:label: *Topic filter* set to: social, work_life
:bell: *Reminder delay* set to `10 minutes`
:pencil: Prompt creation invite sent to @username.
```

### Time input format

The App Home time-entry actions accept:

```text
HH:MM:SS AM/PM
```

Example:

```text
09:15:00 AM
```

---

## preset_time_selection

### Purpose
Lets the user choose one of the predefined preset times from a Slack static select menu.

### Behavior
- Maps a selected option like `time_1`, `time_2`, and so on to a real preset time value.
- Saves both the selected preset id and resolved daily target time.

### Success Feedback
`:clock1: Preset time set to {time}`

## active_days_selection


### Purpose
Determines which weekdays the scheduled prompt system is active.

### Accepted Values
- Monday
- Tuesday
- Wednesday
- Thursday
- Friday
- Saturday
- Sunday

### Success Feedback
`:calendar: Active days set to: {day_list}`

---

## Frontend Data Contract

The Slack frontend sends or receives these main values:

- `team_id`: identifies the Slack workspace
- `channel_id`: identifies the active Slack channel
- `user_id`: identifies the user interacting with the bot
- `text`: raw slash command text or manual time input
- `selected_option.value`: selected value from radio buttons or static selects
- `selected_options`: selected days from checkbox inputs

---

## Validation Rules

- Channel arguments for `/setchannel` must begin with `#`.
- `/picktime` requires an integer in the supported preset range.
- App Home time fields must match `HH:MM:SS AM/PM`.
- Preset control values must map to a known preset option.

---

## Error Handling Expectations

At the frontend contract level, all errors should be understandable to the user.

Current implemented behavior includes:

- Slack-visible validation messages for invalid slash command input
- direct-message validation feedback for invalid App Home time entry
- backend logging for unexpected exceptions

---

## Relationship To Backend API

This frontend contract describes how users interact with VibeCheck through Slack.

The backend HTTP contract in the OpenAPI specification describes how an external system would interact with the service through REST endpoints.

The frontend contract defines the user-facing Slack behavior.
The backend contract defines the system-facing HTTP behavior.
