---
sidebar_position: 2
---

# System Block Diagram

## Overview

This is an illustration of the command flow between each component of VibeCheck, consisting of messaging platforms where users interact, a platform adapter layer that translates platform-specific events, the chatbot core that handles all business logic, and a database that persists user activity and analytics.

![BeReal ChatBot](/img/VibeCheck-SystemBlockDiagram.png)            

## System Flow

Users communicate with VibeCheck through messaging platforms that will deliver message events and slash commands to the chatbot through WebSocket connections. The chatbot processes commands, schedules prompts, selects prompt content, generates responses, sends messages back to the platform via Web API, and stores activity data in MongoDB.

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

### Adapter Layer

The adapter layer translates platform-specific interfaces into a standardized structure for the chatbot to respond appropriately. Currently Slack Bolt provides the Slack adapter, but future adapters will be implemented soon for other message platforms, such as Discord, without changing the chatbot core.