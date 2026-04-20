# src/commands/check_vibes_command.py
import logging
import json
import threading
import os
from datetime import datetime
from datetime import date
from urllib.parse import urlencode

from pymongo import MongoClient
from services.prompt_service import get_random_prompt_text, mark_prompt_asked
from services.mongo_service import get_tracker

def databse_Task(mongo_client, payload, respond, botID, client):
    try:
        db =  mongo_client.get_database("vibecheck")
    except ConnectionError:
        respond(f"MongoDB Connection Failure.")

    try:
        installations_col = db.get_collection("installations")
    except ConnectionError:
        respond(f"Installations collection not found.")
    channel = payload.get("channel_id")  # default to the channel where command was used
    team_id = payload.get("team_id") or (payload.get("authorizations") or [{}])[0].get("team_id") or ""
    team_name = None
    if team_id:
        record = installations_col.find_one({"team_id": team_id})
        if record:
            team_name = record.get("team_name")
    
    collection_name = f"messages_{team_name}" if team_name else f"messages_{team_id or 'unknown'}"
    try:
        messages_col = db.get_collection(collection_name)
    except ConnectionError:
        respond(f"Message Collection Not Connected Successfully")     

    message_array = list(messages_col.find({}))
    prompt_list = organize_data(message_array, botID)
    CurrentDaysVibes = []
    curDate = date.today()
    for vibe in prompt_list:
        vibeDT = datetime.fromisoformat(vibe["time"])
        
        if (vibeDT.day == curDate.day and vibeDT.month == curDate.month and vibeDT.year == curDate.year):
            CurrentDaysVibes.append(vibe)
   
    msg_block = []
    msg_block.append({
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": f"VIBES FOR TODAY ({curDate})",
            "emoji": True
        },
        "level": 1
        }
    )
    msg_block.append({
        "type": "header",
		"text": {
				"type": "plain_text",
				"text": f"VIBES SENT SO FAR: {len(CurrentDaysVibes)}",
				"emoji": True
			},
        "level": 4
        }
    )
   
    forcedVibes = 0
    userCreatedVibes = 0
    randomVibes = 0
    curVibeID = 0
    chartLabels = []
    chartData = []
    for vibe in CurrentDaysVibes:
        if vibe["checkType"] == "forced":
            forcedVibes += 1
        elif vibe["checkType"] == "random":
            randomVibes += 1
        elif vibe["checkType"] == "user-created":
            userCreatedVibes += 1
        curVibeID += 1
        vibeText = vibe["text"]
        vibeTime = vibe["time"]
        vibeReplies = len(vibe["replies"])
        vibeUniqueUsers = len(vibe["unique_users"])
        vibeEngagement = vibe["engagement"]
        chartLabels.append(f"Vibe #{curVibeID}")
        chartData.append(vibeEngagement)
        # msg_block.append({
        #    "type": "section",
		#	"text": {
		#		"type": "mrkdwn",
		#		"text": f"Vibe #{curVibeID} - {vibe["checkType"]}"
		#	},
		#	"accessory": {
		#		"type": "button",
		#		"text": {
		#			"type": "plain_text",
		#			"text": "More Info",
		#			"emoji": True
		#		},
		#		"value": f"{vibeText}",
		#		"action_id": "checkvibes_moreInfo"
		#	}
        # })
        chartConfig = {
            "type": "bar",
            "data": {
                "labels": chartLabels,
                "datasets": [{
                    "label": "Engagement",
                    "data": chartData
                }]
            }
        }

        chartParams = {
            'chart' : json.dumps(chartConfig),
            'width' : 800,
            'height' : 400,
            'backgroundColor': 'white',
        }

        msg_block.append(
            {
			"type": "image",
			"image_url": 'https://quickchart.io/chart?%s' % urlencode(chartParams),
			"alt_text": "delicious tacos"
		    }
        )
        
    #    lines.append(f"\nVibe Prompt: {vibeText}\n  • Time Released {vibeTime}\n • Replies: {vibeReplies}\n • # of Unique Repliers: {vibeUniqueUsers} \n •  Vibe Total Engagement: {vibeEngagement}")

    msg_block.append({
        "type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": f"*Random Vibes:*\n{randomVibes}"
				},
				{
					"type": "mrkdwn",
					"text": f"*Forced Vibes:*\n{forcedVibes}"
				},
				{
					"type": "mrkdwn",
					"text": f"*User-created Vibes:*\n{userCreatedVibes}"
				}
			]
        }
    )
 #   lines.append(f"\nRandom Vibes: {randomVibes}\nForced Vibes: {forcedVibes}\nUser-Created Vibes: {userCreatedVibes}\n")
 #   respond("\n".join(lines))
    
    client.chat_postMessage(channel=channel, blocks=msg_block)
    # for message in message_array :
    #    print(f"Message:{message.get("text")}")

def register_check_vibes_command(bolt_app, state_manager, botID):
    mongo_client = MongoClient(os.getenv("MONGO_URI"))
    # BOT_USERID = 
    @bolt_app.command("/checkvibes")
    def handle_checkvibes(ack, respond, body, client):
        ack("Checking out the vibes...")
        
        threading.Thread(target=databse_Task, args=(mongo_client, body, respond, botID, client)).start()
        # respond("Checking out the Vibes!!")
        # for message in messages_col.find():
        #    message.get()

    @bolt_app.action("checkvibes_moreInfo")
    def handle_action_more_info(ack, body, action, logger):
        ack()
        action_value = action.get("value")

        user_id = body["user"]["id"]
        channel_id = body["channel"]["id"]
        print(f"Clicked Button: {action_value}")

def organize_data(db, bot_id):
    vibe_prompt_list = []
    MaxVibeID = 0
    LatestVibeInstance = None
    for record in db:
        isoString = record.get("ingested_at_utc")
       
        if not record.get("user_id"):
            continue
        
        if (record.get("user_id") == bot_id):
            check_type = None
            if "forced vibe check" in record.get("text"):
                check_type = "forced"
            elif "random vibe check" in record.get("text"):
                check_type = "random"
            elif "user-created vibe check" in record.get("text"):
                check_type = "user-created"

            if check_type:
                vibe_prompt_list.append({
                    "time" : isoString, 
                    "text" : record.get("text"), 
                    "thread": record.get("ts"),
                    "channel": record.get("channel_id"),
                    "vibeID" : (MaxVibeID := MaxVibeID + 1),
                    "checkType": check_type,
                    "replies" : [],
                    "unique_users": [],
                    "engagement" : 0
                    })
                LatestVibeInstance = vibe_prompt_list[len(vibe_prompt_list) - 1]

        else:
            VibeInstance = None
            Replied = False
            if not record.get("thread_ts"):
                # THE MESSAGE SENT DOES NOT REPLY TO A THREAD, THEREFORE IT WILL USE THE LATEST VIBE INSTANCE.
                if LatestVibeInstance:
                    # THERE IS A LATEST VIBE INSTACE, THEREFORE IT WILL ADD ITSELF TO THE REPLIES OF THE CHECK.
                    # SHOULD CONTINUE ONWARDS THOUGH AND NOT RECORD REPLY IF THE MESSAGES ARE NOT IN THE CHANNEL AS THE PROMPT.
                    VibeInstance = LatestVibeInstance
            else:
                # LOOP THROUGH THE AVAILBLE VIBE PROMPTS, COMPARE THE THREAD_TS of the record to the thread value.
                RepliedVibeInstance = None
                for vibe in vibe_prompt_list:
                    if vibe["thread"] == record.get("thread_ts"):
                        RepliedVibeInstance = vibe
                        Replied = True
                        break

                # IF THERE IS A MATCH, THEN ADD MESSAGE TO REPLY AND CANCEL.
                if RepliedVibeInstance:
                    VibeInstance = RepliedVibeInstance
            
            if VibeInstance:
                if VibeInstance["channel"] != record.get("channel_id"):
                    continue

                engageVal = 0
                dt = datetime.fromisoformat(isoString)
                TimeOfVibe = datetime.fromisoformat(VibeInstance["time"])
                secondsBetweenMessages = (dt - TimeOfVibe).total_seconds()
                if record.get("text") != "":
                    engageVal += 10

                if record.get("subtype"):
                    if record.get("subtype") == "file_share":
                        engageVal += 50

                if Replied == True:
                    engageVal += 5

                if secondsBetweenMessages <= 300:
                    engageVal *= 5
                elif secondsBetweenMessages > 300 and secondsBetweenMessages <= 480:
                    engageVal *= 4
                elif secondsBetweenMessages > 300 and secondsBetweenMessages <= 480:
                    engageVal *= 3
                elif secondsBetweenMessages > 480 and secondsBetweenMessages <= 600:
                    engageVal *= 2
                elif secondsBetweenMessages > 600 and secondsBetweenMessages <= 1800:
                    engageVal *= 1
                else:
                    engageVal *= 0

                if secondsBetweenMessages > 1800 and (dt.month != TimeOfVibe.month or dt.year != TimeOfVibe.year or dt.day != TimeOfVibe.day) and Replied == False:
                    # IF THE MESSAGE IS MORE THAN 30 MINUTES FROM THE VIBE INSTANCE
                    # IF THE MESSAGE IS NOT THE SAME MONTH, DAY, OR YEAR
                    # AND THis not a replied message, we will not add this one to the replies.
                    # MESSAGE IS TOO OLD
                    continue
                
                VibeInstance["replies"].append({
                    "time" : isoString,
                    "timeBetweenVibe": secondsBetweenMessages,
                    "text" : record.get("text"),
                    "subtype" : record.get("subtype"),
                    "engagementValue" : engageVal
                })
                if record.get("user_id") not in VibeInstance["unique_users"]:
                    VibeInstance["unique_users"].append(record.get("user_id"))

                VibeInstance["engagement"] += engageVal
    return  vibe_prompt_list
   
    

        