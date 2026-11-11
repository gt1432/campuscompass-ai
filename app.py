"""
CampusCompass AI - University Helpdesk Application
Full-stack Flask application with Google Gemini integration.
"""

import os
import uuid
import time
import logging
from flask import Flask, render_template, request, jsonify

from config import Config
from knowledge_base import CATEGORIES_META
from ai_service import ai_service
from database import db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(name)s: %(message)s"
)
logger = logging.getLogger("CampusCompass.App")

app = Flask(__name__)
app.config["SECRET_KEY"] = Config.FLASK_SECRET_KEY

@app.route("/")
def index():
    """Renders the premium CampusCompass AI landing page."""
    return render_template("index.html", categories=CATEGORIES_META)

@app.route("/api/health", methods=["GET"])
def health():
    """Backend health check reporting AI and Database status."""
    gemini_ready = ai_service.is_available()
    return jsonify({
        "status": "healthy",
        "service": "CampusCompass AI",
        "gemini_connected": gemini_ready,
        "gemini_model": Config.GEMINI_MODEL,
        "database": "MongoDB Atlas" if db.is_connected() else "In-Memory",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Primary chat endpoint.
    Expects JSON: { "message": "...", "session_id": "..." }
    """
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    session_id = data.get("session_id", "").strip()

    if not session_id:
        session_id = str(uuid.uuid4())

    if not message:
        return jsonify({
            "success": False,
            "answer": "Please ask a question regarding academics, attendance, examinations, placements, library, hostel, administration, or events.",
            "category": "General",
            "provider": "System",
            "grounded": True
        }), 400

    # Retrieve prior conversation turns for multi-turn contextual grounding
    history = db.get_history(session_id, limit=6)

    # Save user message
    db.save_message(
        session_id=session_id,
        role="user",
        content=message,
        category="UserQuery",
        provider="User"
    )

    # Generate response
    ai_result = ai_service.get_response(message=message, session_id=session_id, history=history)

    # Save assistant response
    db.save_message(
        session_id=session_id,
        role="assistant",
        content=ai_result.get("answer", ""),
        category=ai_result.get("category", "General"),
        provider=ai_result.get("provider", "Gemini"),
        grounded=ai_result.get("grounded", True)
    )

    return jsonify({
        "success": ai_result.get("success", True),
        "answer": ai_result.get("answer", ""),
        "category": ai_result.get("category", "General"),
        "provider": ai_result.get("provider", "Gemini"),
        "grounded": ai_result.get("grounded", True),
        "session_id": session_id
    })

@app.route("/api/feedback", methods=["POST"])
def feedback():
    """Saves student feedback (Helpful / Not Helpful)."""
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id", "anonymous")
    message_id = data.get("message_id", str(uuid.uuid4()))
    fb_value = data.get("feedback", "helpful")
    query = data.get("query", "")
    response = data.get("response", "")

    db.save_feedback(session_id, message_id, fb_value, query, response)
    return jsonify({"success": True, "message": "Feedback recorded. Thank you!"})

@app.route("/api/clear", methods=["POST"])
def clear_chat():
    """Clears session chat history."""
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id", "")
    if session_id:
        db.clear_session(session_id)
    return jsonify({"success": True, "message": "Conversation history cleared."})

@app.route("/api/categories", methods=["GET"])
def get_categories():
    """Returns the 8 authoritative university help categories."""
    return jsonify({"success": True, "categories": CATEGORIES_META})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", Config.PORT))
    logger.info(f"Starting CampusCompass AI on {Config.HOST}:{port}")
    app.run(host=Config.HOST, port=port, debug=Config.DEBUG)
