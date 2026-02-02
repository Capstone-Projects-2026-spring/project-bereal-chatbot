---
sidebar_position: 2
---

# System Block Diagram
![BeReal ChatBot](/img/BeRealChatBot.drawio.png)


## Description

 This project is a BeReal ChatBot that operates within Slack to connect people in a professional or academic environment. This project will be comprised of Python, the Slack API, Slack Bolt, FastAPI, and SQLite. 
 
 Users interact with the chatbot through a Slack group chat, where they can respond to prompts by submitting messages or images. These interactions are sent from Slack to the FastAPI backend, which handles data manipulation, creates a response for the chatbot, and stores the data in the database. Slack then sends the response back to users or the group chat.

