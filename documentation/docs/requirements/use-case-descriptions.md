---
sidebar_position: 5
---

# Use-Case Descriptions

---

## Use Case 1 — Installing VibeCheck in a Slack Workspace

As a workspace admin, I want to install VibeCheck in Slack so that my team can use bot commands and scheduled prompts.

#### Triggering Event
- The admin opens the Slack install URL for VibeCheck.

#### Normal Flow
1. The admin opens the install link
2. Slack shows the OAuth consent screen
3. The admin approves requested permissions
4. Slack redirects to the OAuth callback endpoint with an authorization code
5. The admin sees a success message

#### Alternate Flows
- If the authorization code is missing, the system returns an error response and the installation is not completed
- If Slack OAuth exchange fails, the system returns the Slack error and no installation record is created

#### Preconditions
- The admin has permission to install apps in the workspace
- The bot server is running and reachable

#### Postconditions
- A workspace installation record exists
- The bot can authenticate for that workspace

---

## Use Case 2 — Setting Active Channel

As a workspace user, I want to set the channel where prompts are posted so that my team receives prompts in the correct place.

#### Triggering Event
- The user runs the `/setchannel` command

#### Normal Flow
1. The user runs `/setchannel #channel-name`
2. The system validates that the input starts with `#`
3. The system resolves the workspace id from the command payload
4. The system stores the selected channel in the workspace state
5. The system stores the active token for that workspace session
6. The system confirms the selected channel to the user
7. The system posts a confirmation message to that channel

#### Alternate Flows
- If no channel is provided, the system responds with usage guidance
- If the channel format is invalid, the system returns a validation message
- If posting confirmation fails, the command still sets state but logs an operational error

#### Preconditions
- The bot is installed in the workspace
- The user can run slash commands

#### Postconditions
- The workspace state includes the active channel
- Future scheduled or forced prompts target the selected channel

---

## Use Case 3 — Configuring Prompt Time

As a workspace user, I want to configure or check the prompt time so that prompts are sent at expected times.

#### Triggering Event
- The user runs `/picktime`

#### Normal Flow
1. The user runs `/picktime` with a preset option number
2. The system validates that the option is numeric and in range
3. The system maps the selected option to a preset time
4. The system stores the selected daily target time in workspace state
5. The system confirms the new scheduled time
6. The user can run `/findtime` to retrieve the current scheduled time

#### Alternate Flows
- If `/picktime` has no argument, the system returns a list of available time options
- If the user is using the dashboard, they can manually select everything using radio buttons and text inputs

#### Preconditions
- The bot is installed in the workspace
- A workspace state exists or can be created

#### Postconditions
- Workspace state contains the updated daily target time

---

## Use Case 4 — Sending Prompts

As a workspace user, I want prompts to be posted automatically or on demand so that the team can participate in daily check-ins.

#### Triggering Event
- Scheduled time is reached, or a user runs `/forceprompt`

#### Normal Flow
1. The prompt is sent because it's the scheduled time or `/forceprompt` was used
2. The system selects a prompt from the prompt catalog
3. The system marks the prompt as "asked" in catalog metadata
4. The system upserts prompt stats and increments ask count
5. The system posts the prompt to the target channel
6. The system records the prompt as active for that channel for response tracking

#### Alternate Flows
- If prompt retrieval fails, the system logs the error and no prompt is posted
- If channel post fails, the system logs the failure and retries on future triggers

#### Preconditions
- The bot is installed and authenticated
- A target channel is available in a workspace channel or a default channel

#### Postconditions
- A prompt message is posted to the channel when successful
- Prompt stats ask counters are updated

---

## Use Case 5 — Viewing Prompt Statistics

As a workspace user, I want to view prompt usage statistics so that I can understand team engagement trends.

#### Triggering Event
- The user runs `/promptstats`

#### Normal Flow
1. The user runs `/promptstats`
2. The system loads prompt statistics sorted by ask count
3. The system formats top prompt entries with ask and response totals
4. The system responds in Slack with the formatted statistics summary

#### Alternate Flows
- If the tracker is not initialized, the system returns an initialization warning
- If no stats exist, the system returns a no-data message

#### Preconditions
- Prompt tracker is initialized
- Prompt stats data exists or can be queried

#### Postconditions
- The user receives the current prompt engagement summary

---

## Use Case 6 — Configuring the Bot via the Control Panel

As a workspace admin, I want to configure all bot settings from a single UI so that I can control scheduling, topics, and features without using slash commands.

#### Triggering Event
- The admin opens the VibeCheck App Home tab in Slack.

#### Normal Flow
1. The admin opens the App Home tab
2. The system renders the control panel with the current workspace configuration
3. The admin modifies one or more settings (operation mode, time, active days, topic filters, prompt type, reminders, or prompt creator assignment)
4. The admin submits the changes
5. The system validates and applies each setting to workspace state
6. The system sends a DM to the admin confirming the updated configuration

#### Alternate Flows
- If a time input is in an invalid format, the system rejects the change and returns a validation error
- If the assigned prompt creator user does not exist, the system returns an error

#### Preconditions
- The bot is installed in the workspace
- The admin has access to the App Home tab

#### Postconditions
- Workspace state reflects the submitted configuration changes
- Future scheduled prompts use the updated settings

---

## Use Case 7 — User-Created Prompt Invitation

As a workspace user, I want to be invited to create the day's prompt so that team members have a voice in daily engagement topics.

#### Triggering Event
- At 9:15 AM, the scheduler randomly selects a channel member (approximately 30% daily probability), or an admin manually assigns a prompt creator via the control panel.

#### Normal Flow
1. The system selects a user and sends them a DM with a "Create Today's Prompt" button
2. The user clicks the button within the 5-minute submission window
3. A modal opens with fields for topic (required), custom prompt text (optional), and send time (optional)
4. The user submits the form
5. The system validates the submission is within the allowed window
6. The system stores the custom prompt and schedules it for the target time (or posts immediately if "Send now" is checked)

#### Alternate Flows
- If the user submits after the 5-minute window has expired, the system rejects the submission with an expiry message
- If no custom text is provided, the system uses the selected topic to pick a matching prompt from the CSV catalog
- If an admin assigns a specific user via the control panel, the DM is sent immediately rather than waiting for the scheduler

#### Preconditions
- A target channel and workspace state are configured
- The selected user is a member of the active channel

#### Postconditions
- A custom or topic-matched prompt is queued for the scheduled post time or sent immediately

---

## Use Case 8 — Tracking Response Streaks

As a workspace user, I want to track and view my consecutive daily response streak so that I stay motivated to engage each day.

#### Triggering Event
- A user runs `/streak` or `/streak leaderboard`.

#### Normal Flow
1. The user runs `/streak`
2. The system reads the structured response log to calculate the user's consecutive daily response days
3. The system formats the streak count with the appropriate milestone emoji
4. The system responds with the user's current streak
5. If the streak meets a milestone (7, 14, 21, 50, 100, 365, or 730 days), the system posts an announcement in the active channel

#### Alternate Flows
- If the user runs `/streak leaderboard`, the system returns the top 10 users ranked by current streak
- If no response log entries exist for the user, the system returns a zero-streak message

#### Preconditions
- The structured log file is accessible and contains response entries
- The bot is installed in the workspace

#### Postconditions
- The user receives their current streak count
- Milestone announcements are posted to the channel when applicable

---

## Use Case 9 — Social Connector

As a workspace user, I want the bot to introduce me to a teammate with shared interests so that I can build new connections on the team.

#### Triggering Event
- At 2:00 PM, the scheduler fires the social connector (approximately 50% daily probability), or a user runs `/connect`.

#### Normal Flow
1. The system queries MongoDB for all users with stored interest tags in the workspace
2. The system finds two users who share at least one interest tag
3. The system uses the LLM service to generate a personalized introduction message referencing their shared interests
4. The system posts the introduction message in the active channel tagging both users

#### Alternate Flows
- If no users share matching tags, the system skips or uses a generic pairing
- If the LLM service is unavailable, the system falls back to a default introduction template
- If fewer than two users have registered interests, the social connector does not fire

#### Preconditions
- At least two users in the workspace have registered interest tags via `/picktags`
- A target channel is configured

#### Postconditions
- An introduction message is posted in the active channel pairing two users

---

## Use Case 10 — Mentor-Mentee Program

As a workspace user, I want to sign up as a mentor or mentee and be matched with a partner so that I can grow professionally within my team.

#### Triggering Event
- A user runs `/mentor signup [mentor|mentee]`, `/mentor match`, or an admin opens the mentor admin panel.

#### Normal Flow (User Signup and Matching)
1. The user runs `/mentor signup mentor` or `/mentor signup mentee`
2. A modal opens with fields for job title, years of experience, bio, and interest tags
3. The user submits the form and their profile is saved in MongoDB
4. An admin runs `/mentor match` or uses the admin panel to trigger matching
5. The system runs a greedy matching algorithm pairing mentors and mentees by shared interests (with fallback for unmatched users)
6. For each new pair, the system creates a Slack group DM and sends personalized AI-generated introduction messages to both users
7. On Mondays at 9:00 AM, the scheduler sends a weekly check-in message to all active pairs

#### Alternate Flows
- If a user runs `/mentor status`, the system returns their current role, profile, and matched partner (if any)
- If a user runs `/mentor leave`, their profile and pairing are removed
- If an admin opens `/mentor admin`, they see all profiles and pairing status, and can manually pair any two users
- If the LLM service is unavailable, a default introduction message is used

#### Preconditions
- The bot is installed in the workspace
- The user is not already registered in the program

#### Postconditions
- The user's profile is stored in MongoDB scoped to the workspace
- Matched pairs have a shared group DM and have received introduction messages

---

## Use Case 11 — Late Response Reminders

As a workspace admin, I want the bot to remind users who have not responded to the daily prompt so that participation rates stay high.

#### Triggering Event
- Approximately 30 seconds after a scheduled prompt is posted (when reminders are enabled in workspace state).

#### Normal Flow
1. The system retrieves the list of members in the active channel
2. The system checks the structured response log for users who have already responded to the current prompt
3. For each non-responding, non-bot member, the system sends a DM reminding them to respond

#### Alternate Flows
- If reminders are disabled in workspace state, the system skips this step entirely
- If a user's account no longer exists or is a bot, the system skips that user silently

#### Preconditions
- A prompt has been posted and its timestamp recorded in workspace state
- Reminders are enabled via the control panel
- A target channel is configured

#### Postconditions
- Each non-responding eligible member has received a reminder DM

---

## Use Case 12 — AI-Powered Reactions and Replies

As a workspace user, I want the bot to react and reply to my prompt responses so that the channel feels more engaging and interactive.

#### Triggering Event
- A user posts a message or image in the active channel in response to the daily prompt.

#### Normal Flow
1. The bot receives the message event for the active channel
2. The system records the response in the structured log and increments the response count in MongoDB
3. If LLM reactions are enabled and the probability check passes, the system calls the LLM service with the prompt context and the user's message (including image data if applicable)
4. The LLM returns a valid Slack emoji name; the bot adds the reaction to the message
5. If LLM replies are enabled and the probability check passes, the system calls the LLM service to generate a short, casual 1–2 sentence reply
6. The bot posts the reply in the channel thread

#### Alternate Flows
- If the LLM API returns an error or times out, the system skips the reaction or reply silently and logs the failure
- If the returned emoji name is invalid for Slack, the system falls back to a default emoji
- If reactions or replies are disabled via environment configuration, the system skips those steps entirely

#### Preconditions
- The bot is installed and listening for message events in the workspace
- A prompt has been posted and recorded as active for the channel

#### Postconditions
- The response is logged and counted toward prompt statistics and the user's streak
- An emoji reaction and/or reply may be added depending on configuration and probability

