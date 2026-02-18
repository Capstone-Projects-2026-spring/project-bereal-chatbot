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

The system is built using a Pytho processes Slack events through the Slack API. database is used to persist user data, prompts, submissions, timestamps, and late flags, enabling consistent tracking and retrieval of shared content. Communication between Slack and the backend, where Slack acts as the user interface and the FastAPI service serves as the application logic layer.

## High Level Requirement

VibeCheck is a chatbot that uses messaging platforms to operate. It sends prompts that will have a timed response others will reply to. Once sent, users can see each other's posts and responses. It is a Slack-integrated chatbot designed to encourage social interaction within professional or academic environments. The chatbot periodically sends time-limited prompts to users during designated break periods, such as lunch breaks. Users respond to these prompts by submitting short text updates and optional images with captions directly through Slack.

Interaction with VibeCheck occurs entirely within Slack channels using standard messaging features and bot commands. Once a response window closes, users are able to view each other’s submissions within the same channel, promoting sociability while maintaining a professional tone. The system automatically enforces timing constraints, manages submissions, and provides feedback to users without requiring a separate application or external interface.

## Conceptual Design

VibeCheck follows a client–server, event-driven architecture. Slack serves as the user interaction layer, where users receive prompts and submit responses. Python is the backend that validates incoming requests, applies business rules such as submission deadlines, processes text and image data, and sends responses back to Slack. Persistent data is stored in database. Stored data includes user data, daily prompts, submissions, timestamps, and late submission flags. This project is designed to run in Slack.

## Background 

Social check-in applications such, as BeReal, encourages authenticity and breaking down superficial barriers. This is done by having users take a time-bounded photo of what they're doing and of themselves, but they are primarily designed for mobile and personal social contexts. VibeCheck adapts this concept to professional and academic environments by providing similar functionalities within Slack. Unlike BeReal, which relies on a dedicated mobile frontend, VibeCheck operates entirely through an existing messaging interface, reducing friction and encouraging participation during natural breaks in the workday.

## Required Resources

To develop VibeCheck, background knowledge in Python, APIs, databases is necessary, along with familiarity with event-driven application design. Software resources include Python, any IDE, and access to Slack.

No hardware requirements. Resources are commonly available within standard Computer Science department environments.

## Collaborators

<div align="center">

[//]: # (Replace with your collaborators)
[Justin Pham](https://github.com/Prismfade) • [Khai Thach](https://github.com/Khai-Thach) • [John Livezey](https://github.com/Jawn654) • [Chris Breeden](https://github.com/CRBreeden) • [Nathan Hollick](https://github.com/) • [Carl Pierre-Louis](https://github.com/carlpielou03)

</div>
