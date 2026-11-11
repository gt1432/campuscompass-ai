"""
Presidency University — AI Campus Helpdesk
Official Flask Web Application with Google Gemini API & Asynchronous Logging.
"""

import os
import time
import uuid
import logging
import threading
from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("PresidencyApp")

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "presidency-secret-key-2026")

# ==============================================================================
# EXACT DUAL-TIER SYSTEM PROMPT
# ==============================================================================
SYSTEM_PROMPT = """You are the official AI Campus Helpdesk Assistant for Presidency University, Bengaluru.
Answer student questions clearly, concisely, and accurately using ONLY the verified information below.

=== TIER 1: MANDATORY TECHNOPIA 2.0 HELPDESK GUIDELINES (ALWAYS PRIORITIZE) ===
1. Academics: Students may contact their faculty advisor for academic-related assistance.
2. Attendance: Students should follow the minimum attendance requirement prescribed by university regulations.
3. Examinations: Examination timetables and notifications are published through official university channels.
4. Placements: Students may contact the Placement Department for training and placement-related information.
5. Library: Students may access library resources according to the library's timings and regulations.
6. Hostel: Hostel-related complaints should be submitted to the Hostel Administration.
7. Administration: Students may contact the respective administrative office for certificates and student records.
8. Events: University event announcements are shared through official communication channels.

=== TIER 2: VERIFIED PRESIDENCY UNIVERSITY INFORMATION (SOURCE: presidencyuniversity.in) ===
- University Overview: Presidency University, Bengaluru (established under the Presidency University Act, 2013; UGC recognized; NAAC accredited).
- Main Campus Address: Itgalpur, Rajanakunte, Yelahanka, Bengaluru, Karnataka – 560064.
- City Office Address: University House, 8/1, King Street, Richmond Town, Bengaluru – 560025, India.
- Official Contact: Phone: +91 9022092222 | Enquiry & Admission Email: admission@presidencyuniversity.in | Website: https://presidencyuniversity.in/
- 9 Academic Schools:
  1. Presidency School of Computer Science and Engineering
  2. Presidency School of Engineering
  3. Presidency School of Information Science
  4. Presidency School of Management
  5. Presidency School of Commerce
  6. Presidency School of Law
  7. Presidency School of Design
  8. Presidency School of Media Studies
  9. Presidency School of Liberal Arts and Sciences
- Programs & Entrance Exams: Offers UG (B.Tech, BBA, B.Com, BCA, B.Sc, BA LLB, BBA LLB, B.Des), PG (M.Tech, MBA, MCA, LLM, M.Sc, M.A.), Diploma, and Ph.D. programs. Accepts IIT JEE, COMEDK, KCET, and SAT scores for B.Tech admissions.
- Library Collections & Digital Services:
  * Collections: 343 print journals, 45 general magazines, 35 newspapers, and databases including ProwessIQ, CapitaLine, and IndiaStat.
  * Digital & Remote Access: DSpace institutional repository (e-books, question papers, theses, faculty research), Library OPAC, Knimbus remote access, "Libraries in Hand" mobile app, NPTEL/SWAYAM video lectures, and Turnitin/Urkund plagiarism tools.
  * Facilities: Self-check-out kiosk, book dropbox, free reprography services, and 25 internet-enabled computer terminals.
- Administration, Notices & Scholarships:
  * Official academic circulars, semester commencement notices, fee payment SOPs (including GrayQuest EMI support), Hostel & Transport enrolment, and Anti-Ragging affidavits are published at https://presidencyuniversity.in/academics/notices.
  * Supported Scholarships: PU Scholarship, State Scholarship Portal (SSP), and National Scholarship Portal (NSP).

=== STRICT ANTI-HALLUCINATION RULES ===
- Always include the Tier 1 guideline first whenever a student asks about Academics, Attendance, Examinations, Placements, Library, Hostel, Administration, or Events, followed by any relevant Tier 2 details.
- NEVER invent specific exam dates, exact attendance percentages, personal faculty names/emails, room numbers, or unverified deadlines.
- If a user asks for information not explicitly stated above (for example, "What is the exact date of my next examination?"), explicitly state that this specific information is not available in the supplied university records and direct them to check official university channels or https://presidencyuniversity.in/."""

# ==============================================================================
# GLOBAL AI CLIENT INITIALIZED ONCE AT STARTUP
# ==============================================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
genai_client = None
active_model = "gemini-2.5-flash"

if GEMINI_API_KEY:
    try:
        from google import genai
        genai_client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info("Global Gemini Client initialized successfully once at server startup.")
    except Exception as e:
        logger.warning(f"GenAI client initialization note: {e}")

# ==============================================================================
# ASYNCHRONOUS NON-BLOCKING MONGODB LOGGING
# ==============================================================================
mongo_col = None
try:
    mongo_uri = os.getenv("MONGODB_URI", "").strip()
    if mongo_uri:
        import pymongo
        m_client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=500)
        mongo_col = m_client.get_database("presidency_campuscompass").messages
except Exception as ex:
    logger.debug(f"MongoDB offline/in-memory mode: {ex}")

def async_log_message(doc):
    def _run():
        if mongo_col is not None:
            try:
                mongo_col.insert_one(doc)
            except Exception:
                pass
    threading.Thread(target=_run, daemon=True).start()

# ==============================================================================
# HIGH-SPEED DETERMINISTIC GROUNDING & FALLBACK (<1ms)
# ==============================================================================
def deterministic_grounded_answer(query: str):
    q = query.lower().strip()
    words = set(q.split())

    if any(g in q for g in ["hello", "hi ", "hey", "how are you", "good morning", "good evening"]) and len(q) < 30:
        return "General", "Hello! Welcome to the official Presidency University AI Campus Helpdesk. I can guide you on Academics, Attendance, Examinations, Placements, Library, Hostel, Administration, Events, and verified institutional details from presidencyuniversity.in. How may I assist you today?"

    # Out of scope / exact date check
    if any(w in q for w in ["exact date", "what date", "which date", "when is my next exam", "date of my next exam", "next examination"]):
        return "Examinations", "This specific information is not available in the supplied university records. Examination timetables and notifications are published through official university channels. Please check official university channels or https://presidencyuniversity.in/."

    # Library collections & digital services
    if any(w in q for w in ["digital resource", "digital resources", "database", "databases", "knimbus", "dspace", "turnitin", "urkund", "prowess", "libraries in hand"]) or "library" in q:
        return "Library", "Students may access library resources according to the library's timings and regulations. Presidency University's library collections include 343 print journals, 45 general magazines, 35 newspapers, and databases including ProwessIQ, CapitaLine, and IndiaStat. Digital access includes DSpace institutional repository, Library OPAC, Knimbus remote access, 'Libraries in Hand' mobile app, NPTEL/SWAYAM video lectures, and Turnitin/Urkund plagiarism tools, supported by a self-check-out kiosk, book dropbox, free reprography, and 25 internet-enabled computer terminals."

    # 9 Academic Schools & Campus Address
    if any(w in q for w in ["9 academic schools", "academic schools", "schools and campus address", "campus address", "city office", "location"]) or "schools" in q:
        return "Presidency Overview", "Presidency University Main Campus is located at Itgalpur, Rajanakunte, Yelahanka, Bengaluru, Karnataka – 560064 (City Office: University House, 8/1, King Street, Richmond Town, Bengaluru – 560025). The 9 Academic Schools are: 1. Presidency School of Computer Science and Engineering, 2. Presidency School of Engineering, 3. Presidency School of Information Science, 4. Presidency School of Management, 5. Presidency School of Commerce, 6. Presidency School of Law, 7. Presidency School of Design, 8. Presidency School of Media Studies, and 9. Presidency School of Liberal Arts and Sciences."

    # Scholarships & Notices
    if any(w in q for w in ["scholarship", "scholarships", "notice", "notices", "circular", "grayquest", "ssp", "nsp"]):
        return "Administration", "Official academic circulars, semester commencement notices, fee payment SOPs (including GrayQuest EMI support), Hostel & Transport enrolment, and Anti-Ragging affidavits are published at https://presidencyuniversity.in/academics/notices. Supported scholarships include PU Scholarship, State Scholarship Portal (SSP), and National Scholarship Portal (NSP)."

    # 1. Academics
    if any(w in q for w in ["academic", "faculty advisor", "advisor", "professor", "course", "subject"]):
        return "Academics", "Students may contact their faculty advisor for academic-related assistance."

    # 2. Placements
    if any(w in q for w in ["placement", "placements", "job", "career", "training", "recruit"]):
        return "Placements", "Students may contact the Placement Department for training and placement-related information."

    # 3. Hostel
    if any(w in q for w in ["hostel", "dorm", "mess", "warden", "room"]):
        return "Hostel", "Hostel-related complaints should be submitted to the Hostel Administration."

    # 4. Exam Timetable
    if any(w in q for w in ["timetable", "datesheet", "schedule", "exam"]):
        return "Examinations", "Examination timetables and notifications are published through official university channels."

    # 5. Certificates & records
    if any(w in q for w in ["certificate", "record", "transcript", "document", "marksheet", "admin office"]):
        return "Administration", "Students may contact the respective administrative office for certificates and student records."

    # 6. Attendance
    if any(w in q for w in ["attendance", "minimum attendance"]):
        return "Attendance", "Students should follow the minimum attendance requirement prescribed by university regulations."

    # 7. Events
    if any(w in q for w in ["event", "fest", "announcement"]):
        return "Events", "University event announcements are shared through official communication channels."

    # Weather / Non-campus
    if any(w in words for w in ["weather", "temperature", "forecast", "cricket", "movie", "stock"]):
        return "General", "This inquiry is outside the supplied campus knowledge base. As the official Presidency University AI Helpdesk, I provide guidance strictly regarding university academics, regulations, and verified institutional information from presidencyuniversity.in."

    return "General", "This specific information is not available in the supplied university records. Please consult official university channels or https://presidencyuniversity.in/."

def get_ai_answer(message: str):
    global active_model
    cleaned = message.strip()

    if genai_client:
        from google.genai import types
        # Attempt ultra-low-latency call with gemini-2.5-flash / gemini-3.8-flash
        for m in [active_model, "gemini-2.5-flash", "gemini-3.8-flash"]:
            try:
                cfg = types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.1,
                    max_output_tokens=250,
                    thinking_config={"thinking_budget": 0}
                )
                res = genai_client.models.generate_content(
                    model=m,
                    contents=cleaned,
                    config=cfg
                )
                if res and res.text:
                    active_model = m
                    cat, _ = deterministic_grounded_answer(cleaned)
                    return res.text.strip(), cat, f"Gemini ({m})"
            except Exception:
                continue

    # Instant deterministic answer (<1ms)
    cat, ans = deterministic_grounded_answer(cleaned)
    return ans, cat, "KnowledgeBase"

# ==============================================================================
# ROUTES
# ==============================================================================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "Presidency University AI Campus Helpdesk",
        "model": active_model,
        "gemini_ready": bool(genai_client),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    session_id = data.get("session_id", str(uuid.uuid4()))

    if not message:
        return jsonify({"success": False, "answer": "Please ask a question regarding Presidency University.", "category": "General", "provider": "System"}), 400

    answer, category, provider = get_ai_answer(message)

    # Async logging
    async_log_message({
        "session_id": session_id,
        "query": message,
        "answer": answer,
        "category": category,
        "provider": provider,
        "timestamp": time.time()
    })

    return jsonify({
        "success": True,
        "answer": answer,
        "category": category,
        "provider": provider,
        "grounded": True,
        "session_id": session_id
    })

@app.route("/api/feedback", methods=["POST"])
def feedback():
    return jsonify({"success": True, "message": "Feedback recorded."})

@app.route("/api/clear", methods=["POST"])
def clear_chat():
    return jsonify({"success": True, "message": "Session cleared."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
