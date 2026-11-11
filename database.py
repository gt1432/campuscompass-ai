import os
import time
import logging
import threading
from config import Config

logger = logging.getLogger("Presidency.DB")

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.messages_col = None
        self.feedback_col = None
        self.memory_history = {}
        self.memory_feedback = []
        self._connected = False
        
        # Initialize connection in non-blocking thread so server boots instantaneously
        threading.Thread(target=self._init_mongo, daemon=True).start()

    def _init_mongo(self):
        uri = Config.MONGODB_URI.strip() if Config.MONGODB_URI else ""
        if not uri:
            return

        try:
            import pymongo
            self.client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=500)
            self.client.admin.command('ping')
            self.db = self.client.get_database("presidency_campuscompass")
            self.messages_col = self.db.messages
            self.feedback_col = self.db.feedback
            self._connected = True
            logger.info("Connected to MongoDB Atlas asynchronously.")
        except Exception as e:
            logger.warning(f"MongoDB offline/unreachable: {e}. Running in-memory.")
            self._connected = False

    def is_connected(self):
        return self._connected

    def save_message(self, session_id: str, role: str, content: str, category: str = "General", provider: str = "Gemini", grounded: bool = True):
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
        
        # In-memory instant append
        if session_id not in self.memory_history:
            self.memory_history[session_id] = []
        self.memory_history[session_id].append(doc)

        # Asynchronous non-blocking MongoDB write
        if self._connected and self.messages_col is not None:
            def _async_insert(d):
                try:
                    self.messages_col.insert_one(d.copy())
                except Exception as ex:
                    logger.debug(f"Async Mongo insert skipped: {ex}")
            threading.Thread(target=_async_insert, args=(doc,), daemon=True).start()

        return doc

    def get_history(self, session_id: str, limit: int = 8):
        # Fast memory return
        return self.memory_history.get(session_id, [])[-limit:]

    def save_feedback(self, session_id: str, message_id: str, feedback: str, query: str = "", response: str = ""):
        doc = {
            "session_id": session_id,
            "message_id": message_id,
            "feedback": feedback,
            "query": query,
            "response": response,
            "timestamp": time.time()
        }
        self.memory_feedback.append(doc)
        if self._connected and self.feedback_col is not None:
            threading.Thread(target=lambda: self.feedback_col.insert_one(doc.copy()), daemon=True).start()
        return True

    def clear_session(self, session_id: str):
        if session_id in self.memory_history:
            self.memory_history[session_id] = []
        if self._connected and self.messages_col is not None:
            threading.Thread(target=lambda: self.messages_col.delete_many({"session_id": session_id}), daemon=True).start()
        return True

db = Database()
print("database.py updated with non-blocking asynchronous logging!")
