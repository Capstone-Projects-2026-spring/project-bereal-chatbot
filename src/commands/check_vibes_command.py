# src/commands/check_vibes_command.py
import logging
import json
import threading
import os

from pymongo import MongoClient
from services.prompt_service import get_random_prompt_text, mark_prompt_asked
from services.mongo_service import get_tracker



def databse_Task(mongo_client, payload, respond, botID):
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

    respond("Checking the Vibes!!")
    message_array = list(messages_col.find({}))
    print(len(message_array))
    print(message_array[len(message_array) - 1])
    # while message_cursor.hasNext():
    #    curMsg = message_cursor.Next()
    #    record = json.loads(curMsg)
    #    respond(f"Message Record: {record.get("text")}")
    # for message in message_array :
    #    print(f"Message:{message.get("text")}")

def register_check_vibes_command(bolt_app, state_manager, botID):
    mongo_client = MongoClient(os.getenv("MONGO_URI"))
    # BOT_USERID = 
    @bolt_app.command("/checkvibes")
    def handle_checkvibes(ack, respond, body, client):
        ack("Checking out the vibes...")
        
        threading.Thread(target=databse_Task, args=(mongo_client, body, respond, botID)).start()
        # respond("Checking out the Vibes!!")
        # for message in messages_col.find():
        #    message.get()


        

        