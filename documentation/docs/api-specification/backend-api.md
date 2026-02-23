---
sidebar_position: 1
description: Backend API Design Docuement
---

Backend API - Design Document - Part II API
=============================

# Purpose

This Design Document gives the complete design of the software implementation. This information should be in structured comments (e.g. Javadoc) in the source files. We encourage the use of a documentation generation tool to generate a draft of your API that you can augment to include the following details.

Language: Python
Tools: slack_sdk, dotenv

The purpose of the Backend API is to present how Vibecheck solves the way of working with Slack's API. We've laid out some current functions that are made for the Slack app currently.

# Requirements

In addition to the general documentation requirements the Design Document - Part II API will contain:

![BeReal ChatBot](/img/BeRealChatBot.drawio.png)

<details>
<summary>Functional - Using Slack Token:</summary>
    
- Using Dotenv, the system is able to recieve and send messages with Slack, allowing the program to interact with Slack.
- Token is set through .env (which has to be created by the user itself because of token security)
  
</details>

<details>
<summary>Functional - Start/End Notification:</summary>
    
- Will probably be removed from final product
- Allow users to know when product is usable through Slack

</details>


<details>
<summary>Functional - Random Time Library:</summary>
    
- Switch cases of preset times that is picked randomly.
- Uses "hh:mm:ss" time format

</details>

<details>
<summary>Functional - Chatbot Controls:</summary>
    
- Function to add prompts that is isolated to a specific Slack server
- Admin controls to set time and frequencies of chatbot sending prompts (once a day or many times)
- Leaderboard kept to show users how frequent they interact with Vibecheck

</details>

<details>
<summary>Functional - Data Collection:</summary>
    
- For leaderboards and streaks, frequencies of response to Vibecheck is collected

</details>


<details>
<summary>Functional - Prompts:</summary>
    
- Vibecheck sends text-based prompts that is to be responded by users and are encouraged to post text/pictures.

</details>

<details>
<summary>Nonfunctional - Scalability:</summary>
    
- Encouraged to work with different platforms such as Discord,, Slack, SMS, etc...
- Handle many requests and responses
- Collect information and responses for leaderboard system instantly
- Remain consistent (.env) to scale with many other platforms

</details>

<details>
<summary>Nonfunctional - Security:</summary>
    
- Ensure that users know what data we are collecting
- Make sure that authentication key is not leaked

</details>

### Classes
**For each class define the data fields, methods.**

<details>
<summary>getenv("SLACK_TOKEN):</summary>
    
- Purpose: Recieves the token from .env to allow program to connect to Slack.

### Functional - Prompts:
- Vibecheck sends text-based prompts that is to be responded by users and are encouraged to post text/pictures.


### Nonfunctional - Scalability
- Encouraged to work with different platforms such as Discord,, Slack, SMS, etc...
- Handle many requests and responses.
- Collect information and responses for leaderboard system instantly.
- Remain consistent (.env) to scale with many other platforms.


### Nonfunctional - Security
- Ensure that users know what data we are collecting.
- Make sure that authentication key is not leaked.

</details>


<details>
<summary>display_current_time():</summary>
    
- Purpose: In terminal, display the corresponding time

# Data Field and Methods

## Bot.py - Class
## getenv("SLACK_TOKEN"):
### Purpose
Recieves the token from .env to allow program to connect to Slack.

### Pre-conditions
Requires slack_sdk and dotenv.

### Post-conditions
Allows program to connect and interact with Slack application.

### Returns
Does not return anything.

</details>

<details>
<summary>preSet_time_library(random_number):</summary>
    
- Purpose: Contains library of different preset times

### Exceptions Thrown
Catch when .env is not thrown, but can proceed to check terminal functions.

## def display_current_time() -> str:

### Purpose 
In terminal, display the corresponding time.

### Pre-conditions 
Uses datetime, must be imported.

### Post-conditions
Current time is printed and updated.

### Returns
String of current time in "%I:%M:%S %p" format.

### Output 
Returns string of time in hh:mm:ss "(AM/PM)" format.

### Exceptions Thrown 
Checks if parameter is a integer.
</details>

<details>
<summary>Requerements for each class</summary>
The purpose of the class.
The purpose of each data field.
The purpose of each method
Pre-conditions if any.
Post-conditions if any.
Parameters and data types
Return value and output variables
Exceptions thrown
</details>
