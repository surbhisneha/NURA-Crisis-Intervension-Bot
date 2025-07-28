import os
from cloudant.client import Cloudant
from cloudant.error import CloudantException
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()

CLOUDANT_USERNAME = os.getenv("CLOUDANT_USERNAME")
CLOUDANT_API_KEY = os.getenv("CLOUDANT_API_KEY")
CLOUDANT_URL = os.getenv("CLOUDANT_URL")

DB_NAME = "chat_history"

def get_db():
    client = Cloudant.iam(
        account_name=CLOUDANT_USERNAME,
        api_key=CLOUDANT_API_KEY,
        url=CLOUDANT_URL,
        connect=True
    )
    db = client.create_database(DB_NAME, throw_on_exists=False)
    return db

def save_chat_to_cloudant(user_id, user_input, bot_response, mood="neutral"):
    db = get_db()
    db.create_document({
        "user_id": user_id,
        "message": user_input,
        "response": bot_response,
        "mood": mood,
        "type": "chat",
        "timestamp": datetime.utcnow().isoformat()  # ✅ Add timestamp
    })
def load_last_mood(user_id):
    db = get_db()
    user_docs = [
        doc for doc in db
        if doc.get("user_id") == user_id and doc.get("type") == "chat"
    ]
    if not user_docs:
        return "neutral"

    # ✅ Sort using timestamp
    sorted_docs = sorted(user_docs, key=lambda d: d.get("timestamp", ""), reverse=True)
    return sorted_docs[0].get("mood", "neutral")
