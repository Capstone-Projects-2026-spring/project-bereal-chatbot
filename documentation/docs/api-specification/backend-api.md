---
sidebar_position: 1
description: Backend API Design Document
---

# Backend API - Design Document - Part II API
=============================

## Purpose

This page documents the backend API as a set of resources, requests, and responses.

---

## Scope

VibeCheck has one backend-facing interface; a Slack Bolt runtime that powers the bot.


Formal HTTP contract is maintained in:

- `documentation/static/openapi.yml.yaml`

The rendered version appears in:

- `docs/api-specification/openapi-spec`

---

## API Style

- Protocol: HTTPS/JSON
- Format: REST-style resource endpoints
- Authentication: bearer token for protected endpoints
- Primary resources: prompts, submissions, admin actions, metrics

---

## Resource Overview

| Resource | Description | Access Pattern |
| --- | --- | --- |
| Health | service availability and version metadata | `GET /health` |
| Prompt | active prompt and prompt delivery data | `GET /v1/prompts/today` |
| Submission | user response to a prompt | `POST /v1/submissions` |
| Admin Prompt Dispatch | manual prompt send operation | `POST /v1/admin/prompts/force-send` |
| Prompt Metrics | prompt usage counts and response counts | `GET /v1/metrics/prompts` |

---

## Endpoint Summary

| Method | Path | Input | Output |
| --- | --- | --- | --- |
| `GET` | `/health` | none | service status, version, timestamp |
| `GET` | `/v1/prompts/today` | auth header | active prompt metadata |
| `POST` | `/v1/submissions` | JSON request body | created submission record |
| `POST` | `/v1/admin/prompts/force-send` | JSON request body | queued dispatch result |
| `GET` | `/v1/metrics/prompts` | query parameters and auth header | list of prompt metrics |

---

## Metrics Data

This is the part the critique was asking for: the API specification should clearly show what metrics data exists and how it is accessed through the REST API.

### Prompt Metrics Fields

The backend tracks prompt-usage metrics per workspace. Each prompt metric record contains:

- `teamId`: Slack workspace identifier
- `promptId`: unique prompt identifier
- `prompt`: prompt text
- `tags`: associated topic tags
- `timesAsked`: number of times the prompt has been posted
- `timesResponded`: number of responses recorded for that prompt
- `lastAskedAt`: timestamp of the most recent send

### Metrics Access Pattern

Clients retrieve metrics through:

```text
GET /v1/metrics/prompts?teamId=T12345&limit=20
```

### Example Metrics Response

```json
{
	"teamId": "T12345",
	"count": 2,
	"items": [
		{
			"promptId": "5",
			"prompt": "If you had to swap jobs with a friend for a day, who would it be?",
			"tags": ["work_life"],
			"timesAsked": 8,
			"timesResponded": 5,
			"lastAskedAt": "2026-04-13T18:30:00Z"
		},
		{
			"promptId": "12",
			"prompt": "Post a photo that captures your current energy.",
			"tags": ["photo", "social"],
			"timesAsked": 6,
			"timesResponded": 2,
			"lastAskedAt": "2026-04-12T18:30:00Z"
		}
	]
}
```
---

## Request and Response Examples

### `GET /v1/prompts/today`

**Response**

```json
{
	"promptId": "prm_20260330",
	"text": "Post a quick lunch update and a photo.",
	"channelId": "C01234567",
	"opensAt": "2026-03-30T16:00:00Z",
	"closesAt": "2026-03-30T16:30:00Z",
	"status": "active"
}
```

### `POST /v1/submissions`

**Request**

```json
{
	"userId": "U12345",
	"channelId": "C01234567",
	"text": "Lunch break at the student center",
	"imageUrl": "https://cdn.example.com/images/submission1.jpg"
}
```

**Response**

```json
{
	"submissionId": "sub_4f8128",
	"promptId": "prm_20260330",
	"userId": "U12345",
	"channelId": "C01234567",
	"text": "Lunch break at the student center",
	"imageUrl": "https://cdn.example.com/images/submission1.jpg",
	"createdAt": "2026-03-30T16:11:33Z",
	"late": false
}
```

### `POST /v1/admin/prompts/force-send`

**Request**

```json
{
	"channelId": "C01234567",
	"promptText": "Share one photo that shows your current vibe.",
	"postImmediately": true
}
```

**Response**

```json
{
	"requestId": "req_7dc2e1",
	"status": "queued"
}
```
---

## Error Contract

Protected endpoints may return:

- `401 Unauthorized` when authentication is missing or invalid
- `403 Forbidden` when the caller lacks permission for an admin endpoint
- `400 Bad Request` when the input payload is invalid
- `409 Conflict` when a submission duplicates an existing prompt response
- `500 Internal Server Error` for unexpected failures