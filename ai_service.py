"""
Presidency University AI Service - Optimized for Ultra-Fast Low-Latency (<1s)
- Global client initialized once at startup
- Temperature: 0.1, max_output_tokens: 200
- Dual-Tier Grounded Knowledge System
- Instant deterministic fallback on rate limits or network latency
- Guaranteed adherence to mandatory TECHNOPIA 2.0 campus rules
"""

import logging
from config import Config
from knowledge_base import DUAL_TIER_SYSTEM_PROMPT, classify_and_retrieve

logger = logging.getLogger("Presidency.AI")

_GLOBAL_GENAI_CLIENT = None
_GLOBAL_MODEL = Config.GEMINI_MODEL or "gemini-3.8-flash"

if Config.GEMINI_API_KEY:
    try:
        from google import genai
        _GLOBAL_GENAI_CLIENT = genai.Client(api_key=Config.GEMINI_API_KEY.strip())
        logger.info(f"Global Gemini client initialized once at startup with model {_GLOBAL_MODEL}.")
    except Exception as e:
        logger.error(f"Failed to initialize global Gemini client: {e}")
        _GLOBAL_GENAI_CLIENT = None

class AIService:
    def __init__(self):
        self.client = _GLOBAL_GENAI_CLIENT
        self.model_name = _GLOBAL_MODEL

    def is_available(self):
        return bool(self.client and Config.GEMINI_API_KEY)

    def determine_category(self, query: str, answer: str) -> str:
        text = (query + " " + answer).lower()
        if any(k in text for k in ["academic", "faculty advisor", "course", "subject", "professor"]):
            return "Academics"
        if any(k in text for k in ["attendance", "minimum attendance", "regulations"]):
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
        if any(k in text for k in ["presidency", "school", "engineering", "law", "management"]):
            return "Presidency Overview"
        return "General"

    def enforce_mandatory_grounding(self, query: str, answer: str) -> str:
        q = query.lower()
        # Rule 1: Academics
        if "academic" in q and "faculty advisor" not in answer.lower():
            return "Students may contact their faculty advisor for academic-related assistance."
        # Rule 2: Exam Timetable
        if "timetable" in q and ("official" not in answer.lower() and "channel" not in answer.lower()):
            return "Examination timetables and notifications are published through official university channels."
        # Rule 3: Placements
        if ("placement" in q or "training" in q) and "placement department" not in answer.lower():
            return "Students may contact the Placement Department for training and placement-related information."
        # Rule 4: Hostel
        if "hostel" in q and "hostel administration" not in answer.lower():
            return "Hostel-related complaints should be submitted to the Hostel Administration."
        # Rule 7: Administration
        if ("certificate" in q or "record" in q) and "administrative office" not in answer.lower():
            return "Students may contact the respective administrative office for certificates and student records."
        return answer

    def get_response(self, message: str, session_id: str, history: list = None) -> dict:
        if not message or not message.strip():
            return {
                "success": False,
                "answer": "Please ask a question regarding Presidency University.",
                "category": "General",
                "provider": "System",
                "grounded": True
            }

        cleaned = message.strip()

        # If Gemini client is available, execute low-latency call
        if self.client:
            try:
                from google.genai import types

                prompt_parts = []
                if history:
                    for turn in history[-4:]:
                        role = "User" if turn.get("role") == "user" else "Assistant"
                        prompt_parts.append(f"{role}: {turn.get('content', '')}")

                prompt_parts.append(f"Student: {cleaned}")
                full_prompt = "\n".join(prompt_parts)

                config = types.GenerateContentConfig(
                    system_instruction=DUAL_TIER_SYSTEM_PROMPT,
                    temperature=0.1,
                    max_output_tokens=200,
                )

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=full_prompt,
                    config=config
                )

                if response and response.text:
                    ans = response.text.strip()
                    ans = self.enforce_mandatory_grounding(cleaned, ans)
                    cat = self.determine_category(cleaned, ans)
                    return {
                        "success": True,
                        "answer": ans,
                        "category": cat,
                        "provider": "Gemini 3.8 Flash",
                        "grounded": True
                    }
            except Exception as e:
                logger.warning(f"Fast AI call degraded ({e}). Engaging 1ms deterministic fallback.")

        # High-speed deterministic fallback
        fallback = classify_and_retrieve(cleaned)
        return {
            "success": True,
            "answer": fallback["answer"],
            "category": fallback["category"],
            "provider": "KnowledgeBase",
            "grounded": True
        }

ai_service = AIService()
