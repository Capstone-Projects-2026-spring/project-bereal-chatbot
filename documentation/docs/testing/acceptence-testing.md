---
sidebar_position: 3
---
# Acceptance test

Acceptance testing demonstrates that functional and non-functional requirements are met through manual execution and recorded observations. It is also automated by running pytest from the project root to execute tests and report pass/fail results.

### Acceptance tests should be documented using this spreadsheet:

[Download Acceptance QA Testing Doc.xlsx](/Acceptance%20QA%20Testing%20Doc.xlsx)

---

| Type | Category | Requirement | Procedure | Outcome |
|------|----------|-------------|-----------|---------|
| F-1 | Chatbot Controls | Users can create their own prompts | Attempt to create a custom prompt through available user controls in Slack. | User-generated prompts can be created and used by the bot. |
| F-2 | Chatbot Controls | Chatbot must enforce quick-time events | Configure prompt timing mode. Verify prompt behavior around configured windows. | Prompt timing is constrained by configured/preset windows. |
| F-3 | Chatbot Controls | Chatbot must send a message once a day that encourages team engagement | Set active channel and schedule. Observe daily prompt delivery. | One daily engagement prompt is posted to configured channel. |
| F-4 | Chatbot Controls | Chatbot must group users based on post details | Trigger grouping workflow based on user content. | Users are grouped by post details. |
| F-5 | Chatbot Controls | Chatbot must display a leaderboard of streak scores | Run leaderboard or streak summary flow. | Ranked streak leaderboard is returned. |
| F-6 | Data Collection | Track how many times each user responds | Send multiple user replies after a prompt. Query analytics/statistics output. | Response counts are tracked and visible. |
| F-7 | Data Collection | Track individual user streak scores | Simulate daily participation for one user. | User streak is updated and retrievable. |
| F-8 | Data Collection | Track late posts | Submit responses after expected window. | Late posts are flagged and stored. |
| F-9 | Data Collection | Track missed posts | Leave prompt unanswered during cycle. | Missed post event is tracked. |
| F-10 | Prompts | Make picture-based prompts | Trigger prompt generation repeatedly. Verify image-type prompts are selected. | Image-oriented prompt types are produced. |
| F-11 | Prompts | Make text-based prompts | Trigger prompt generation and inspect message content. | Text prompts are generated and posted. |
| F-12 | Prompts | Make photo-encouraged prompts | Review generated prompt content for photo encouragement language. | Prompts encouraging photo responses are present. |
| F-13 | Prompts | Make text-encouraged prompts | Review generated prompt content for text response language. | Prompts encouraging text responses are present. |
| NF-1 | Scalability | Available on multiple messaging platforms | Review architecture implementation and adapter extension points. Attempt onboarding for a second platform (prototype stage). | Platform abstraction supports extension beyond Slack. |
| NF-2 | Scalability | Handle large numbers of requests/responses | Run high-volume message simulation in staging. | Bot remains responsive and records events correctly. |
| NF-3 | Scalability | Respond to events near-instantly | Send slash commands and message events. Measure response latency. | Responses occur within acceptable latency threshold. |
| NF-4 | Scalability | Remain consistent via environment-based configuration | Run deployment/startup in two environments with different env var values. Verify the bot loads environment-specific values correctly. | Environment-driven configuration works consistently across environments. |
| NF-5 | Security | Ensure stored data is secure and minimize loss/duplication/corruption | Validate upsert-based writes for installation/prompt stats. Validate failure-path logging for DB write errors. | Writes are controlled and idempotent where designed. |
| NF-6 | Security | Ensure events do not lose data or repeat prompts | Observe repeated cycles across day boundaries. Verify prompt posting and event logging consistency. | Event handling remains consistent without unintended duplicate prompts. |



