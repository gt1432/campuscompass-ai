"""
CampusCompass AI - AI Service
Integrates with Google Gemini API via official google-genai SDK.
Enforces strict grounding, intent classification, and graceful fallback.
"""

import logging
import re
from config import Config
from knowledge_base import SYSTEM_PROMPT, classify_and_retrieve

logger = logging.getLogger("CampusCompass.AI")

class AIService:
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY.strip() if Config.GEMINI_API_KEY else ""
        self.model_name = Config.GEMINI_MODEL or "gemini-3.8-flash"
        self.client = None
        self._init_client()

    def _init_client(self):
        if not self.api_key:
            logger.warning("No GEMINI_API_KEY detected. AI service will use authoritative offline fallback.")
            return

        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            logger.info(f"Gemini client initialized with model '{self.model_name}'.")
        except Exception as e:
            logger.error(f"Error initializing Google GenAI client: {e}")
            self.client = None

    def is_available(self):
        return bool(self.client and self.api_key)

    def determine_category(self, query: str, answer: str) -> str:
        text = (query + " " + answer).lower()
        if any(k in text for k in ["academic", "faculty advisor", "course", "subject", "professor"]):
            return "Academics"
        if any(k in text for k in ["attendance", "minimum attendance", "shortage", "regulations"]):
            return "Attendance"
        if any(k in text for k in ["exam", "examination", "timetable", "schedule"]):
            return "Examinations"
        if any(k in text for k in ["placement", "job", "career", "training", "internship", "placement department"]):
            return "Placements"
        if any(k in text for k in ["library", "book", "reading room", "library resources"]):
            return "Library"
        if any(k in text for k in ["hostel", "room", "mess", "hostel administration", "complaint"]):
            return "Hostel"
        if any(k in text for k in ["certificate", "record", "transcript", "administrative office", "bonafide"]):
            return "Administration"
        if any(k in text for k in ["event", "announcement", "fest", "communication channel"]):
            return "Events"
        return "General"

    def get_response(self, message: str, session_id: str, history: list = None) -> dict:
        """
        Generates a grounded response to a student question using Gemini API
        or authoritative knowledge-base fallback.
        """
        if not message or not message.strip():
            return {
                "success": False,
                "answer": "Please enter a question so I can assist you.",
                "category": "General",
                "provider": "System",
                "grounded": True
            }

        cleaned_message = message.strip()

        # If Gemini client is active, call Gemini with grounding
        if self.client:
            try:
                from google.genai import types
                
                # Format conversation history for context
                contents = []
                if history:
                    for turn in history[-6:]:
                        role = turn.get("role", "user")
                        content = turn.get("content", "")
                        # Map to user/model roles
                        g_role = "user" if role == "user" else "model"
                        contents.append(f"{g_role.capitalize()}: {content}")
                
                contents.append(f"Student: {cleaned_message}")
                full_prompt = "\n".join(contents)

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.2,
                        max_output_tokens=600,
                    )
                )

                if response and response.text:
                    answer_text = response.text.strip()
                    category = self.determine_category(cleaned_message, answer_text)
                    return {
                        "success": True,
                        "answer": answer_text,
                        "category": category,
                        "provider": "Gemini",
                        "grounded": True
                    }
                else:
                    logger.warning("Empty response received from Gemini API.")
            except Exception as e:
                logger.error(f"Gemini API request failed: {e}. Falling back to knowledge-base engine.")

        # Authoritative Knowledge Base Fallback
        fallback = classify_and_retrieve(cleaned_message)
        return {
            "success": True,
            "answer": fallback["answer"],
            "category": fallback["category"],
            "provider": "KnowledgeBase (Offline Fallback)",
            "grounded": True
        }

ai_service = AIService()
