---
sidebar_position: 1
description: What should be in this section.
---

Design Document - Part II API
=============================

**Purpose**

This Design Document gives the complete design of the software implementation. This information should be in structured comments (e.g. Javadoc) in the source files. We encourage the use of a documentation generation tool to generate a draft of your API that you can augment to include the following details.

**Requirements**

In addition to the general documentation requirements the Design Document - Part II API will contain:

General review of the software architecture for each module specified in Design Document - Part I Architecture. Please include your class diagram as an important reference.

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
