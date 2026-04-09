---
sidebar_position: 1
description: Frontend API Design Docuement
---

Frontend API - Design Document - Part II API
=============================

# Purpose

This document defines the frontend contract for VibeCheck.

For this project, the frontend is not a browser application. The frontend is the Slack user interface that users interact with through:

- slash commands
- App Home controls
- bot-posted messages in Slack channels
- direct-message feedback from the bot

This contract explains what the Slack-facing interface accepts, what it returns to the user, and how the backend responds to valid and invalid inputs.

Language: Slack UI / Slack Bolt
Tools: Slack slash commands, Slack App Home, Block Kit components
<<<<<<< deploychris
=======

---
>>>>>>> main

# Requirements

The frontend API contract must stay synchronized with the actual Slack interaction behavior implemented by the bot.

This includes:

- supported slash commands
- expected command parameters
- validation rules for user input
- bot responses shown in channels or direct messages
- App Home interactive controls and their effects
- error messages that are meaningful to the user

<<<<<<< deploychris
=======
---

>>>>>>> main
## Frontend Surface Overview

VibeCheck exposes the following user-facing interaction points in Slack:

1. `/findtime`
2. `/picktime`
3. `/setchannel`
4. `/forceprompt`
5. App Home control panel interactions

<<<<<<< deploychris
=======
---

>>>>>>> main
## Slack Slash Commands

| Command | Input Pattern | Primary Behavior | Success Response |
| --- | --- | --- | --- |
| `/findtime` | `/findtime` | Returns the currently scheduled prompt time for the workspace | `Today's random scheduled prompt time is {time}` |
| `/picktime` | `/picktime <number>` | Sets daily target time from preset option `1` through `11` | `Time set to: {daily_target_time}` |
| `/setchannel` | `/setchannel #channel-name` | Sets active posting/listening channel and posts channel confirmation | `Active channel set to #channel-name` |
| `/forceprompt` | `/forceprompt [text\|image] [#channel-name]` | Posts a random prompt immediately, optionally filtered and channel-targeted | `Posted a prompt to {channel}.` |

---

## /findtime

### Purpose
Returns the currently scheduled prompt time for the workspace.

### Input
No arguments.

### Processing
The command resolves the Slack workspace team id, loads the stored team state, and reads the current daily target time.

### Success Response
The bot responds in Slack with:

`Today's random scheduled prompt time is {time}`

### Preconditions
- The bot must be installed in the Slack workspace.
- Workspace state must be available.

### Error Behavior
- If an exception occurs, the command currently logs the error to the backend console.
- No user-facing recovery message is guaranteed by the current implementation.

---

## /picktime

### Purpose
Allows an administrator or user to choose a preset prompt time from a numbered list.

### Input
`/picktime <number>`

### Accepted Parameters
- `number` must be an integer from `1` to `11`.

### Behavior
- If no argument is provided, the bot returns the list of available numbered time choices.
- If the argument is a valid number in range, the corresponding preset time is stored as the new daily target time.
- If the argument is not numeric, the bot responds with a validation error.
- If the number is outside the valid range, the bot responds with a range error.

### Success Response
`Time set to: {daily_target_time}`

### Validation Responses
- `Please provide a valid number between 1 and 11 to set the time`
- `Must pick a number between 1 and 11 to set the time.`

### Output Variables
- Updated daily target time in workspace state.

---

## /setchannel

### Purpose
Sets the Slack channel that the bot will actively listen to and post updates to.

### Input
`/setchannel #channel-name`

### Accepted Parameters
- Channel value must begin with `#`.

### Behavior
- Saves the selected channel to workspace state.
- Stores the active Slack token for the current session.
- Posts a confirmation message directly into the selected channel.

### Success Responses
- Slash command response: `Active channel set to #channel-name`
- Channel message: `The bot will now listen to this channel`

### Validation Responses
- `Please provide a channel name using /setchannel #channel-name`
- `Please provide a valid channel name starting with #`

### Output Variables
- Active channel in workspace state.

---

## /forceprompt

### Purpose
Immediately posts a prompt to the current or specified Slack channel.

### Input Forms
- `/forceprompt`
- `/forceprompt text`
- `/forceprompt image`
- `/forceprompt #channel-name`
- `/forceprompt text #channel-name`
- `/forceprompt image #channel-name`

### Accepted Parameters
- `text` or `image` to filter prompt type
- optional `#channel-name` to override the current channel

### Behavior
- Chooses a random prompt from the prompt service.
- Marks that prompt as asked.
- Records the prompt in tracking storage if tracking is enabled.
- Posts the prompt to Slack with the prefix `Forced vibe check prompt:`.

### Success Response
`Posted a prompt to {channel}.`

### Error Response
`Failed to post prompt: {exception}`

### Output Variables
- Prompt posted to Slack channel.
- Prompt tracking metadata updated if tracker exists.

---

## App Home Control Panel

The App Home tab provides a persistent control panel for time configuration.
<<<<<<< deploychris

### Purpose
Allows an administrator to configure scheduling behavior without typing slash commands.



### UI Sections
1. Operation mode selection
2. Random time range start
3. Random time range end
4. Preset time selection
5. Static manual time entry
6. Active day checkboxes
=======

### Purpose
Allows an administrator to configure scheduling behavior without typing slash commands.



### UI Sections
1. Operation mode selection
2. Random time range start
3. Random time range end
4. Preset time selection
5. Static manual time entry
6. Active day checkboxes

### Operation Modes
- `Random Time`
- `Preset Time Select`
- `Static Set Time`

### Interactive Actions

mode_selection

Changes the scheduling mode stored in team state.

Success feedback is sent by direct message:

`:gear: Operation mode changed to {value}`

If the selected mode is random mode, the system may immediately repick the current daily target time.

---

## start_time

### Input Format
`HH:MM:SS AM/PM`

### Purpose
Sets the beginning of the random time range.

### Success Feedback
`:clock1: Random range start set to {time}`

### Validation Error
`:x: Invalid start time {value} — must be HH:MM:SS AM/PM`

---

## end_time

### Input Format
`HH:MM:SS AM/PM`

### Purpose
Sets the end of the random time range.

### Success Feedback
`:clock1: Random range end set to {time}`

### Validation Error
`:x: Invalid end time {value} — must be HH:MM:SS AM/PM`

---

## static_entry

### Input Format
`HH:MM:SS AM/PM`

### Purpose
Sets a manual fixed time for prompt scheduling.

### Success Feedback
`:clock1: Static time set to {time}`

### Validation Error
`:x: Invalid static time {value} — must be HH:MM:SS AM/PM`

---

## preset_time_selection

### Purpose
Lets the user choose one of the predefined preset times from a Slack static select menu.

### Behavior
- Maps a selected option like `time_1`, `time_2`, and so on to a real preset time value.
- Saves both the selected preset id and resolved daily target time.

### Success Feedback
`:clock1: Preset time set to {time}`
>>>>>>> main

### Operation Modes
- `Random Time`
- `Preset Time Select`
- `Static Set Time`

<<<<<<< deploychris
### Interactive Actions

mode_selection

Changes the scheduling mode stored in team state.

Success feedback is sent by direct message:

`:gear: Operation mode changed to {value}`

If the selected mode is random mode, the system may immediately repick the current daily target time.

---

## start_time

### Input Format
`HH:MM:SS AM/PM`

### Purpose
Sets the beginning of the random time range.

### Success Feedback
`:clock1: Random range start set to {time}`

### Validation Error
`:x: Invalid start time {value} — must be HH:MM:SS AM/PM`

---

## end_time

### Input Format
`HH:MM:SS AM/PM`

### Purpose
Sets the end of the random time range.

### Success Feedback
`:clock1: Random range end set to {time}`

### Validation Error
`:x: Invalid end time {value} — must be HH:MM:SS AM/PM`

---

## static_entry

### Input Format
`HH:MM:SS AM/PM`

### Purpose
Sets a manual fixed time for prompt scheduling.

### Success Feedback
`:clock1: Static time set to {time}`

### Validation Error
`:x: Invalid static time {value} — must be HH:MM:SS AM/PM`

---

## preset_time_selection

### Purpose
Lets the user choose one of the predefined preset times from a Slack static select menu.

### Behavior
- Maps a selected option like `time_1`, `time_2`, and so on to a real preset time value.
- Saves both the selected preset id and resolved daily target time.

### Success Feedback
`:clock1: Preset time set to {time}`


=======
>>>>>>> main
<summary>active_days_selection</summary>


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
