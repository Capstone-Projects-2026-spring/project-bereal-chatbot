---
sidebar_position: 2
---

# System Block Diagram

## Overview

This is an illustration of the command flow between each component of VibeCheck. The system is Slack-specific, having users interact in Slack. Slack Bolt app handles routing and command events, the chatbot core runs business logic, and MongoDB persists activity and analytics.

```mermaid
flowchart TD
    classDef ext fill:#0F172A,stroke:#334155,color:#94A3B8
    classDef http fill:#1E3A5F,stroke:#2563EB,color:#fff
    classDef state fill:#1E3A5F,stroke:#2563EB,color:#fff
    classDef cmd fill:#3B1F5E,stroke:#7C3AED,color:#fff
    classDef svc fill:#134E2A,stroke:#16A34A,color:#fff
    classDef sched fill:#4C1D1D,stroke:#DC2626,color:#fff
    classDef data fill:#1C1917,stroke:#78716C,color:#A8A29E

    SLACK(["Slack API"]):::ext
    MONGO(["MongoDB"]):::ext
    GROQ(["Groq LLM\nmeta-llama / mixtral"]):::ext
    CSV(["prompts.csv"]):::ext
    RAILWAY(["Railway\nCloud Host"]):::ext

    SLACK -->|"POST /slack/events"| RAILWAY
    RAILWAY --> BOLT

    subgraph CORE["Core Application"]
        direction TB

        BOLT["Slack Bolt\nEvent Router"]:::http

        SM["StateManager\n─────────────────\nteam_id → BotState\n• active_channel\n• target_time\n• response_type\n• reminder_enabled\n• last_prompt_ts"]:::state

        BOLT <-->|"per workspace"| SM
    end

    subgraph CMDS["Slash Commands"]
        direction LR
        C1["/forceprompt\nimage / text / any"]:::cmd
        C2["/mentor\nsignup / admin / match"]:::cmd
        C3["/picktags\n/picktopic"]:::cmd
        C4["App Home\nControl Panel"]:::cmd
        C5["/checkvibes\n/promptstats\n/vibestatus"]:::cmd
    end

    BOLT -->|"routes"| CMDS

    subgraph SVCS["Services"]
        direction LR
        PS["PromptService\nCSV cache\ntag + type filter"]:::svc
        MS["MentorService\nregistrations\ngreedy matching"]:::svc
        LS["LLM Service\nemoji reactions\nreplies / intros"]:::svc
        MGS["MongoService\nPromptTracker\nUserInterests"]:::svc
    end

    CSV -->|"cached on boot"| PS
    GROQ <-->|"API"| LS
    MONGO <-->|"read / write"| MS
    MONGO <-->|"read / write"| MGS

    CMDS --> SVCS

    subgraph SCHED["Background Scheduler  (every 1s)"]
        direction LR
        S1["9:15 AM\nUser Prompt\nInvite — 30%"]:::sched
        S2["2:00 PM\nSocial\nConnector — 50%"]:::sched
        S3["9:00 AM Mon\nMentor\nCheck-in"]:::sched
        S4["Daily Target\nVibe Check\nPrompt"]:::sched
        S5["T + 30s\nReminder\nDMs"]:::sched
    end

    SM -->|"reads config"| SCHED
    S4 -->|"get_random_prompt\nresponse_type filter"| PS
    S4 -->|"record_prompt_sent"| MGS
    S2 -->|"get_social_connector_message"| LS
    S3 -->|"get_all_pairs"| MS

    LOG["StructuredLogger\nEvery message\nMongoDB + emoji + reply"]:::svc
    BOLT -->|"event message"| LOG
    LOG --> LS
    LOG --> MGS

    subgraph MFLOW["Mentor Pairing Flow"]
        direction LR
        MR["Profile\nSignup Modal"]:::cmd
        MP["Pair Selected\nadmin / auto-match"]:::cmd
        DM1["Individual DMs\npartner profile + bio"]:::svc
        GDM["Group DM\nBot + Mentor + Mentee\n+ vibe check icebreaker"]:::svc
    end

    C2 --> MFLOW
    MP --> DM1
    MP --> GDM

    DM1 -->|"chat_postMessage"| SLACK
    GDM -->|"conversations_open"| SLACK
    S4 -->|"chat_postMessage"| SLACK
    S5 -->|"conversations_open DM"| SLACK
    S2 -->|"chat_postMessage"| SLACK
    LOG -->|"reactions_add\nchat_postMessage"| SLACK
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