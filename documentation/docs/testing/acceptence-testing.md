---
sidebar_position: 3
---
# Acceptance test

Acceptance testing demonstrates that functional and non-functional requirements are met through manual execution and recorded observations. It is also automated by running pytest from the project root to execute tests and report pass/fail results.

---

## Functional Requirements Testing

### Chatbot Controls

***Users can create their own prompts***

	Procedure:
	- Attempt to create a custom prompt through available user controls in Slack.
	
	Outcome:
	- User-generated prompts can be created and used by the bot.
	

***Chatbot must enforce quick-time events***

	Procedure:
	- Configure prompt timing mode.
	- Verify prompt behavior around configured windows.
	
	Outcome:
	- Prompt timing is constrained by configured/preset windows.
	

***Chatbot must send a message once a day that encourages team engagement***

	Procedure:
	- Set active channel and schedule.
	- Observe daily prompt delivery.
	
	Outcome:
	- One daily engagement prompt is posted to configured channel.
	

***Chatbot must group users based on post details***

	Procedure:
	- Trigger grouping workflow based on user content.
	
	Outcome:
	- Users are grouped by post details.
	

***Chatbot must display a leaderboard of streak scores***

	Procedure:
	- Run leaderboard or streak summary flow.
	
	Outcome:
	- Ranked streak leaderboard is returned.

### Data Collection

***Track how many times each user responds***

	Procedure:
	- Send multiple user replies after a prompt.
	- Query analytics/statistics output.
	
	Outcome:
	- Response counts are tracked and visible.
	

***Track individual user streak scores***

	Procedure:
	- Simulate daily participation for one user.
	
	Outcome:
	- User streak is updated and retrievable.
	

***Track late posts***

	Procedure:
	- Submit responses after expected window.
	
	Outcome:
	- Late posts are flagged and stored.
	

***Track missed posts***

	Procedure:
	- Leave prompt unanswered during cycle.
	
	Outcome:
	- Missed post event is tracked.
	
### Prompts

***Make picture-based prompts***

	Procedure:
	- Trigger prompt generation repeatedly.
	- Verify image-type prompts are selected.
	
	Outcome:
	- Image-oriented prompt types are produced.
	

***Make text-based prompts***

	Procedure:
	- Trigger prompt generation and inspect message content.
	
	Outcome:
	- Text prompts are generated and posted.
	

***FMake photo-encouraged prompts***

	Procedure:
	- Review generated prompt content for photo encouragement language.
	
	Outcome:
	- Prompts encouraging photo responses are present.
	

***Make text-encouraged prompts***

	Procedure:
	- Review generated prompt content for text response language.
	
	Outcome:
	- Prompts encouraging text responses are present.

---

## Non-Functional Requirements Testing

### Scalability

***Available on multiple messaging platforms***

	Procedure:
	- Review architecture implementation and adapter extension points.
	- Attempt onboarding for a second platform (prototype stage).
	
	Outcome:
	- Platform abstraction supports extension beyond Slack.
	

***Handle large numbers of requests/responses***

	Procedure:
	- Run high-volume message simulation in staging.
	
	Outcome:
	- Bot remains responsive and records events correctly.
	

***Respond to events near-instantly***

	Procedure:
	- Send slash commands and message events.
	- Measure response latency.
	
	Outcome:
	- Responses occur within acceptable latency threshold.
	

***Remain consistent via environment-based configuration***

	Procedure:
	- Run deployment/startup in two environments with different env var values.
	- Verify the bot loads environment-specific values correctly.
	
	Outcome:
	- Environment-driven configuration works consistently across environments.
	
### Security

***Ensure stored data is secure and minimize loss/duplication/corruption***

	Procedure:
	- Validate upsert-based writes for installation/prompt stats.
	- Validate failure-path logging for DB write errors.
	
	Outcome:
	- Writes are controlled and idempotent where designed.
	

***Ensure events do not lose data or repeat prompts***

	Procedure:
	- Observe repeated cycles across day boundaries.
	- Verify prompt posting and event logging consistency.
	
	Outcome:
	- Event handling remains consistent without unintended duplicate prompts.
	
