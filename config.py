import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    MONGODB_URI = os.getenv("MONGODB_URI", "")
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "campuscompass-secure-key-2026")
    PORT = int(os.getenv("PORT", 5000))
    HOST = os.getenv("HOST", "0.0.0.0")
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1")
