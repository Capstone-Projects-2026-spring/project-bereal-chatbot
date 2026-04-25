---
sidebar_position: 2
---

# System Block Diagram

## Overview

This is an illustration of the command flow between each component of VibeCheck. The system is Slack-specific, having users interact in Slack. Slack Bolt app handles routing and command events, the chatbot core runs business logic, and MongoDB persists activity and analytics.

```mermaid
flowchart LR
    classDef user fill:#1E3A5F,stroke:#2563EB,color:#fff
    classDef ext fill:#0F172A,stroke:#334155,color:#94A3B8
    classDef bot fill:#4C1D1D,stroke:#DC2626,color:#fff
    classDef cmd fill:#134E2A,stroke:#16A34A,color:#fff
    classDef data fill:#3B1F5E,stroke:#7C3AED,color:#fff

    U(["User"]):::user
    U -->|"types command\nor responds"| SL

    SL(["Slack"]):::ext
    SL -->|"forwards event"| RW

    RW(["Railway\nBot Host"]):::bot
    RW -->|"routes to"| CMD

    subgraph CMD["Bot Actions"]
        direction TB
        C1["Slash Commands"]:::cmd
        C2["Daily Scheduler"]:::cmd
        C3["Auto Reactions & Replies"]:::cmd
    end

    CMD -->|"reads / writes"| DB
    CMD -->|"sends message"| SL
    SL -->|"delivers"| U

    DB(["MongoDB\n+ Groq LLM"]):::data
```
            

## System Flow

Users communicate with VibeCheck through Slack. Slack delivers message events and slash commands through Socket Mode/Web API flows. The chatbot processes commands, schedules prompts, selects prompt content, generates responses, sends messages back to Slack, and stores activity data in MongoDB.

---

## Component Details

#### Slack API
- **Slack Bolt**
The Slack Bolt API allows VibeCheck to handle event routing, command events, and the ability to respond to user actions. Slack Bolt also includes a socket mode adapter, allowing communication without HTTP.
  
- **Slack SDK**
The Slack SDK is a library for Slack API calls, providing the core functionality of how VibeCheck interacts with the platform. Such functionalities include posting prompts, responding to channels, and retrieving server data

---

### Chatbot
The chatbot, VibeCheck, is the core project. It processes slash commands, contains a scheduler to trigger daily prompts, and logs responses to prompts. 

---

### Slack Integration Layer

Slack Bolt and Slack SDK provide the single integration layer for this project. The chatbot core is designed for Slack events and slash commands only.