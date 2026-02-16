---
sidebar_position: 3
---


# Sequence Diagrams 
Sequence diagrams showing the data flow for all use cases. One sequence diagram corresponds to one use case and different use cases should have different corresponding sequence diagrams.

```mermaid
sequenceDiagram
    title: Use Case 1: Reply
    participant User
    participant VibeCheck
    participant Database
    User->>VibeCheck: sends post
    VibeCheck->>Database: store user data
```

```mermaid
sequenceDiagram
    title: Use Case 2: Personal Use
    participant User
    participant Slack
    User->>Slack: select VibeCheck app
    Slack-->>User: Requests user to confirm app selection
    User->>Slack: Confirms request
    Slack-->>User: adds VibeCheck app to the user's group
```

```mermaid
sequenceDiagram
    title: Use Case 3: User Prompts
    participant User
    participant Slack
    User->>Slack: select VibeCheck app
    Slack-->>User: Requests user to confirm app selection
    User->>Slack: Confirms request
    Slack-->>User: adds VibeCheck app to the user's group
```

```mermaid
sequenceDiagram
    title: Use Case 4: Streak History
    participant User
    participant VibeCheck
    participant Database
    User->>VibeCheck: requests streak history
    VibeCheck->>Database: accesses user's data
    Database-->>VibeCheck: returns user's streak data
    VibeCheck-->>User: sends streak history 
```

```mermaid
sequenceDiagram
    title: Use Case 5: Post History
    participant User
    participant VibeCheck
    participant Database
    User->>VibeCheck: requests post history
    VibeCheck->>Database: accesses user's data
    Database-->>VibeCheck: returns user's post data
    VibeCheck-->>User: sends post history 
```

```mermaid
sequenceDiagram
    title: Use Case 6: Peer Connection
    participant User
    participant VibeCheck
    participant Database
    User->>VibeCheck: sends a groupme request
    VibeCheck->>Database: access most activity based on topic
    Database-->>VibeCheck: returns user's topic response data
    VibeCheck-->>User: sends  a list of topic groups to join 
```