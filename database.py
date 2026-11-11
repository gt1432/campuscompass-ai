"""
CampusCompass AI - Database Service
Supports MongoDB Atlas (optional) with automatic in-memory fallback.
"""

import time
import logging
from config import Config

logger = logging.getLogger("CampusCompass.DB")

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.messages_col = None
        self.feedback_col = None
        self.memory_history = {}
        self.memory_feedback = []
        self._connected = False
        
        self._init_mongo()

    def _init_mongo(self):
        uri = Config.MONGODB_URI.strip() if Config.MONGODB_URI else ""
        if not uri:
            logger.info("No MONGODB_URI configured. Running with in-memory session store.")
            return

        try:
            import pymongo
            self.client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=3000)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client.get_database("campuscompass_ai")
            self.messages_col = self.db.messages
            self.feedback_col = self.db.feedback
            self._connected = True
            logger.info("Successfully connected to MongoDB Atlas.")
        except Exception as e:
            logger.warning(f"MongoDB connection failed: {e}. Falling back to in-memory storage.")
            self._connected = False

    def is_connected(self):
        return self._connected

    def save_message(self, session_id: str, role: str, content: str, category: str = "General", provider: str = "System", grounded: bool = True):
        doc = {
            "session_id": session_id,
            "role": role,
            "content": content,
            "category": category,
            "provider": provider,
            "grounded": grounded,
            "timestamp": time.time(),
            "formatted_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if self._connected and self.messages_col is not None:
            try:
                self.messages_col.insert_one(doc)
            except Exception as e:
                logger.error(f"Failed to persist message to MongoDB: {e}")
                
        # In-memory storage
        if session_id not in self.memory_history:
            self.memory_history[session_id] = []
        self.memory_history[session_id].append(doc)
        return doc

    def get_history(self, session_id: str, limit: int = 15):
        if self._connected and self.messages_col is not None:
            try:
                cursor = self.messages_col.find({"session_id": session_id}).sort("timestamp", -1).limit(limit)
                history = list(cursor)
                history.reverse()
                return history
            except Exception as e:
                logger.error(f"Failed to fetch history from MongoDB: {e}")
                
        # Fallback to in-memory
        return self.memory_history.get(session_id, [])[-limit:]

    def save_feedback(self, session_id: str, message_id: str, feedback: str, query: str = "", response: str = ""):
        doc = {
            "session_id": session_id,
            "message_id": message_id,
            "feedback": feedback,
            "query": query,
            "response": response,
            "timestamp": time.time(),
            "formatted_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        if self._connected and self.feedback_col is not None:
            try:
                self.feedback_col.insert_one(doc)
            except Exception as e:
                logger.error(f"Failed to save feedback to MongoDB: {e}")
        self.memory_feedback.append(doc)
        return True

    def clear_session(self, session_id: str):
        if self._connected and self.messages_col is not None:
            try:
                self.messages_col.delete_many({"session_id": session_id})
            except Exception as e:
                logger.error(f"Failed to clear session in MongoDB: {e}")
        if session_id in self.memory_history:
            self.memory_history[session_id] = []
        return True

db = Database()
