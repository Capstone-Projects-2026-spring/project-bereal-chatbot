<div align="center">

# VibeCheck
[![Report Issue on Jira](https://img.shields.io/badge/Report%20Issues-Jira-0052CC?style=flat&logo=jira-software)](https://temple-cis-projects-in-cs.atlassian.net/jira/software/c/projects/DT/issues)
[![Deploy Docs](https://github.com/ApplebaumIan/tu-cis-4398-docs-template/actions/workflows/deploy.yml/badge.svg)](https://github.com/ApplebaumIan/tu-cis-4398-docs-template/actions/workflows/deploy.yml)
[![Documentation Website Link](https://img.shields.io/badge/-Documentation%20Website-brightgreen)](https://applebaumian.github.io/tu-cis-4398-docs-template/)


</div>


## Keywords

Section 1, chatbot application, Python, SQL, Slack Bolt, FastAPI, social connection, future of work 

## Project Abstract

This project presents the design and implementation of a BeReal-inspired chatbot integrated within Slack that aims to form social connections in both professional and academic environments. Vibecheck operates entirely within a messaging platform, allowing users to share short, but time-restricted updates about their day during breaks, such as lunch periods. Users interact with the chatbot through Slack messages, buttons, bot commands, image uploads that enables users to submit photos with captions, or just text in response to daily prompts.

The system is built using a Python-based FastAPI backend that processes Slack events through the Slack API (Slack Bolt). The backend enforces application rules such as submission timing, validates user input, and manages image handling. A SQL-based database is used to persist user data, prompts, submissions, timestamps, and late flags, enabling consistent tracking and retrieval of shared content. Communication between Slack and the backend follows an event-driven, client–server architecture, where Slack acts as the user interface and the FastAPI service serves as the application logic layer.

By leveraging existing messaging platforms, this project demonstrates how social and collaborative experiences can be embedded into professional tools without requiring a dedicated frontend application. The resulting system provides a scalable and extensible foundation for future expansion to additional messaging platforms while maintaining a focus on simplicity, usability, and professional appropriateness.

## High Level Requirement

VibeCheck is a chatbot that uses messaging platforms to operate. It sends prompts that will have a timed response others will reply to. Once sent, users can see each other's posts and responses. It is a Slack-integrated chatbot designed to encourage lightweight social interaction within professional or academic environments. The chatbot periodically sends time-limited prompts to users during designated break periods, such as lunch breaks. Users respond to these prompts by submitting short text updates and optional images with captions directly through Slack.

Interaction with VibeCheck occurs entirely within Slack channels using standard messaging features, bot commands, buttons, and file uploads. Once a response window closes, users are able to view each other’s submissions within the same channel, promoting shared awareness of day-to-day activities while maintaining a professional tone. The system automatically enforces timing constraints, manages submissions, and provides feedback to users without requiring a separate application or external interface.

## Conceptual Design

VibeCheck follows a client–server, event-driven architecture. Slack serves as the user interaction layer, where users receive prompts and submit responses. A Python-based FastAPI backend functions as the application server, receiving events from the Slack API via webhooks. The backend validates incoming requests, applies business rules such as submission deadlines, processes text and image data, and sends formatted responses back to Slack. Persistent data is stored in a SQL database. Stored data includes user identifiers, daily prompts, submissions, timestamps, and late submission flags. The system is designed to run on standard local development machines and may optionally be deployed to a cloud environment. Development is platform-agnostic, supporting common operating systems such as Windows, macOS, or Linux.

## Background

Social check-in applications such as BeReal encourage authentic, time-bounded sharing among users, but they are primarily designed for mobile and personal social contexts. VibeCheck adapts this concept to professional and academic environments by embedding similar functionality within Slack, a widely used workplace communication platform. Unlike BeReal, which relies on a dedicated mobile frontend, VibeCheck operates entirely through an existing messaging interface, reducing friction and encouraging participation during natural breaks in the workday.

Several chatbot frameworks and integrations exist for Slack, including productivity bots and survey tools, but most focus on task management or automation rather than social interaction. Open-source Slack bot frameworks such as Slack Bolt for Python provide foundational infrastructure for event handling but do not offer built-in social sharing workflows. VibeCheck builds upon these tools while implementing custom logic for timed prompts, image handling, and group visibility.

No existing open-source project fully replicates the proposed functionality in a professional messaging environment. Therefore, existing libraries will be used for infrastructure and API interaction, while all application logic and data handling will be custom-developed. Proprietary products such as BeReal inform the conceptual inspiration but are not reused directly.

## Required Resources

To develop VibeCheck, background knowledge in Python, REST APIs, and SQL databases is necessary, along with familiarity with event-driven application design. Documentation for the Slack API, Slack Bolt for Python, and FastAPI will be referenced throughout development.
Software resources include Python, FastAPI, Slack Bolt, a SQL database system, and development tools such as a code editor and Git for version control. A Slack workspace is required for testing and deployment, along with secure storage for API tokens and credentials.

No hardware requirements. Resources are commonly available within standard Computer Science department environments.

## Collaborators

<div align="center">

[//]: # (Replace with your collaborators)
[Justin Pham](https://github.com/Prismfade) • [Khai Thach](https://github.com/Khai-Thach) • [John Livezey](https://github.com/Jawn654) • [Chris Breeden](https://github.com/CRBreeden) • [Nathan Hollick](https://github.com/) • [Carl Pierre-Louis](https://github.com/carlpielou03)

</div>
