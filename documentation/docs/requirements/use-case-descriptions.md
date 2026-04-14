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



