---
sidebar_position: 1
description: Backend API Design Docuement
---

Backend API - Design Document - Part II API
=============================

**Purpose**

This Design Document gives the complete design of the software implementation. This information should be in structured comments (e.g. Javadoc) in the source files. We encourage the use of a documentation generation tool to generate a draft of your API that you can augment to include the following details.

Language: Python

The purpose of the Backend API is to present how Vibecheck solves the way of working with Slack's API. We've laid out some current functions that are made for the Slack app currently.

**Requirements**

In addition to the general documentation requirements the Design Document - Part II API will contain:

![BeReal ChatBot](/img/BeRealChatBot.drawio.png)

Functional - Using Slack Token:
- Using Dotenv, the system is able to recieve and send messages with Slack, allowing the program to interact with Slack.
- Token is set through .env (which has to be created by the user itself because of token security)

Functional - Start/End Notification:
- Will probably be removed from final product
- Allow users to know when product is usable through Slack

Functional - Random Time Library:
- Switch cases of preset times that is picked randomly.
- Uses "hh:mm:ss" time format

Functional - Chatbot Controls:
- Function to add prompts that is isolated to a specific Slack server
- Admin controls to set time and frequencies of chatbot sending prompts (once a day or many times)
- Leaderboard kept to show users how frequent they interact with Vibecheck

Functional - Data Collection:
- For leaderboards and streaks, frequencies of response to Vibecheck is collected

Functional - Prompts:
- Vibecheck sends text-based prompts that is to be responded by users and are encouraged to post text/pictures.

Nonfunctional - Scalability
- Encouraged to work with different platforms such as Discord,, Slack, SMS, etc...
- Handle many requests and responses
- Collect information and responses for leaderboard system instantly
- Remain consistent (.env) to scale with many other platforms

Nonfunctional - Security
- Ensure that users know what data we are collecting
- Make sure that authentication key is not leaked
**For each class define the data fields, methods.**

getenv("SLACK_TOKEN):
    Purpose: Recieves the token from .env to allow program to connect to Slack.

    Pre-conditions: Requires slack_sdk and dotenv

    Post-conditions: Allows program to connect and interact with Slack application

    Returns: Does not return anything

    Output: Allow users to make commands and interactions with Slack client.

def display_current_time():
    Purpose: In terminal, display the corresponding time

    Pre-conditions: Uses datetime, must be imported.

    Post-conditions: Current time is printed and updated.

    Returns: String of current time in "%I:%M:%S %p" format.

    Output: Prints the current time that gets updated every second. Returns current time constantly as well.

def preSet_time_library(random_number):
    Purpose: Contains library of different preset times

    Parameters:
        random_number: A number from main program is selected based on case numbers. Used for selecting a random time from library.

    Pre-conditions: Standalone

    Post-conditions: A random time is chosen and returned

    Returns: String of time in hh:mm:ss "(AM/PM)" format

    Output: Returns string of time in hh:mm:ss "(AM/PM)" format.
The purpose of the class.

The purpose of each data field.

The purpose of each method

Pre-conditions if any.

Post-conditions if any.

Parameters and data types

Return value and output variables

Exceptions thrown\* (PLEASE see note below for details).

An example of an auto-generated and then augmented API specification is here ([Fiscal Design Document 2\_API.docx](https://templeu.instructure.com/courses/106563/files/16928898?wrap=1 "Fiscal Design Document 2_API.docx") )

This group developed their API documentation by hand ([Design Document Part 2 API-1\_MovieMatch.docx](https://templeu.instructure.com/courses/106563/files/16928899?wrap=1 "Design Document Part 2 API-1_MovieMatch.docx") )

\*At the top level, or where appropriate, all exceptions should be caught and an error message that is meaningful to the user generated. It is not OK to say ("xxxx has encountered a problem and will now close (OK?)". Error messages and recovery procedures should be documented in the User’s Manual.
