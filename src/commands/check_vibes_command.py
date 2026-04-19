# src/commands/check_vibes_command.py
import logging
import random
import os

from pymongo import MongoClient
from services.prompt_service import get_random_prompt_text, mark_prompt_asked
from services.mongo_service import get_tracker


def register_check_vibes_command(bolt_app, state_manager):
    mongo_client = MongoClient(os.getenv("MONGO_URI"))
    db = mongo_client.get_database("vibecheck")
    installations_col = db.get_collection("installations")

    @bolt_app.command("/checkvibes")
    def handle_checkvibes(ack, respond, body, client):
        ack()
        if(mongo_client):
            respond(f"Mongo Client has been grabbed.")

            
        respond("STARTING TO Check the Vibes!!")
        channel = body.get("channel_id")  # default to the channel where command was used
        team_id = body.get("team_id") or (body.get("authorizations") or [{}])[0].get("team_id") or ""
        team_name = None
        if team_id:
            record = installations_col.find_one({"team_id": team_id})
            if record:
                respond("Vibes of the records grabbed")
                team_name = record.get("team_name")
            else:
                respond("Could not find the record")
        
        collection_name = f"messages_{team_name}" if team_name else f"messages_{team_id or 'unknown'}"

        if(not db):
            respond(f"There isn't a databse called vibecheck.")
        else:
            respond(f"There is a databse called vibecheck.")

        messages_col = db.get_collection(collection_name)
        if not messages_col:
            respond(f"This channel does not have any logs!")
            return
        else:
            respond(f"This channel does have logs!")

        respond("Checking the Vibes!!")
        # for message in messages_col.find():
        #    message.get()


        

        