---
sidebar_position: 3
---


# sequence diagrams 

#### Use Case 1: Reply
```mermaid
sequenceDiagram

    participant User
    participant VibeCheck
    participant Database
    User->>VibeCheck: sends post
    VibeCheck->>Database: store user data
```

#### Use Case 2: Personal Use
```mermaid
sequenceDiagram
    
    participant User
    participant Slack
    User->>Slack: select VibeCheck app
    Slack-->>User: Requests user to confirm app selection
    User->>Slack: Confirms request
    Slack-->>User: adds VibeCheck app to the user's group
```

#### Use Case 3: User Prompts
```mermaid
sequenceDiagram
    participant User
    participant Slack
    User->>Slack: select VibeCheck app
    Slack-->>User: Requests user to confirm app selection
    User->>Slack: Confirms request
    Slack-->>User: adds VibeCheck app to the user's group
```

#### Use Case 4: Streak History
```mermaid
sequenceDiagram
    participant User
    participant VibeCheck
    participant Database
    User->>VibeCheck: requests streak history
    VibeCheck->>Database: accesses user's data
    Database-->>VibeCheck: returns user's streak data
    VibeCheck-->>User: sends streak history 
```

#### Use Case 5: Post History
```mermaid
sequenceDiagram
    participant User
    participant VibeCheck
    participant Database
    User->>VibeCheck: requests post history
    VibeCheck->>Database: accesses user's data
    Database-->>VibeCheck: returns user's post data
    VibeCheck-->>User: sends post history 
```

#### Use Case 6: Peer Connection
```mermaid
sequenceDiagram
    participant User
    participant VibeCheck
    participant Database
    User->>VibeCheck: sends a groupme request
    VibeCheck->>Database: access most activity based on topic
    Database-->>VibeCheck: returns user's topic response data
    VibeCheck-->>User: sends  a list of topic groups to join 
```