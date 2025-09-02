from typing import List, Dict, Any
from pymongo import MongoClient, ASCENDING
from pymongo.errors import PyMongoError
import time
import os
from dotenv import load_dotenv
from src.config import settings

load_dotenv()


class MongoDBConversationStore:
    def __init__(self, uri: str, db_name: str = "nl2sql", collection_name: str = "conversations"):
        self.uri = uri or os.getenv("MONGODB_URI")
        self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        # Ensure index for efficient queries
        self.collection.create_index([("session_id", ASCENDING), ("ts", ASCENDING)])

    def append(self, session_id: str, role: str, content: str):
        try:
            doc = {
                "session_id": session_id,
                "role": role,
                "content": content,
                "ts": int(time.time())
            }
            self.collection.insert_one(doc)
        except PyMongoError as e:
            # Log error in production
            raise RuntimeError(f"Failed to append conversation: {e}")

    def get(self, session_id: str, last_n: int = 10) -> List[Dict[str, Any]]:
        try:
            cursor = (
                self.collection
                .find({"session_id": session_id})
                .sort("ts", -1)
                .limit(last_n)
            )
            return list(cursor)[::-1]  # Return in chronological order
        except PyMongoError as e:
            # Log error in production
            raise RuntimeError(f"Failed to get conversation: {e}")

    def clear(self, session_id: str):
        try:
            result = self.collection.delete_many({"session_id": session_id})
            if result.deleted_count == 0:
                raise KeyError(f"Session ID '{session_id}' not found in store.")
        except PyMongoError as e:
            # Log error in production
            raise RuntimeError(f"Failed to clear conversation: {e}")

# Global instance for production use
memory = MongoDBConversationStore(uri=settings.MONGO_URI)
