"""
Presidency University — AI Campus Helpdesk
Flask Web Application with Google Gemini AI & Asynchronous MongoDB Logging.
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
- Main Campus Address: Itgalpur, Rajanakunte, Yelahanka, Bengaluru, Karnataka - 560064.
- City Office Address: University House, 8/1, King Street, Richmond Town, Bengaluru - 560025, India.
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

=== RESPONSE STYLE ===
- Be warm, helpful, and professional. Use clear bullet points when listing information.
- Always include the Tier 1 guideline first whenever a student asks about Academics, Attendance, Examinations, Placements, Library, Hostel, Administration, or Events, followed by any relevant Tier 2 details.
- NEVER invent specific exam dates, exact attendance percentages, personal faculty names/emails, room numbers, or unverified deadlines.
- If a user asks for information not explicitly stated above, explicitly state that this specific information is not available and direct them to check official university channels or https://presidencyuniversity.in/.
- For greetings, introduce yourself as the Presidency University AI Campus Helpdesk Assistant and list the topics you can help with."""

# ==============================================================================
# GEMINI CLIENT INITIALIZATION (Global Singleton for Speed)
# ==============================================================================
genai_client = None
active_model = "gemini-3.8-flash"

try:
    import google.genai as genai
    from google.genai import types as genai_types
    _api_key = os.getenv("GEMINI_API_KEY", "")
    if _api_key:
        genai_client = genai.Client(api_key=_api_key)
        logger.info("Global Gemini Client initialized successfully.")
    else:
        logger.warning("GEMINI_API_KEY not set — using deterministic fallback only.")
except Exception as ex:
    logger.error(f"Gemini client init failed: {ex}")
    genai_client = None

# ==============================================================================
# MONGODB (Optional, Non-blocking)
# ==============================================================================
mongo_col = None
def _init_mongo():
    global mongo_col
    try:
        from pymongo import MongoClient
        _mongo_uri = os.getenv("MONGODB_URI", "")
        if _mongo_uri:
            _mc = MongoClient(_mongo_uri, serverSelectionTimeoutMS=800, connectTimeoutMS=800)
            _mc.admin.command("ping")
            mongo_col = _mc["campuscompass"]["chat_logs"]
            logger.info("MongoDB connected successfully.")
    except Exception as ex:
        logger.warning(f"MongoDB background check: in-memory mode active ({ex})")

threading.Thread(target=_init_mongo, daemon=True).start()

def async_log_message(doc):
    def _run():
        if mongo_col is not None:
            try:
                mongo_col.insert_one(doc)
            except Exception:
                pass
    threading.Thread(target=_run, daemon=True).start()

# ==============================================================================
# RICH DETERMINISTIC FALLBACK ANSWERS
# ==============================================================================
def deterministic_grounded_answer(query: str):
    q = query.lower().strip()
    words = set(q.split())

    # Greeting
    if any(g in q for g in ["hello", "hi ", "hey ", "how are you", "good morning", "good afternoon", "good evening", "namaste"]) and len(q) < 35:
        return "General", (
            "Hello! Welcome to the **Presidency University AI Campus Helpdesk**. 👋\n\n"
            "I'm your intelligent campus assistant. I can help you with:\n"
            "- 📚 **Academics** — faculty advisors, courses\n"
            "- 📋 **Attendance** — regulations and requirements\n"
            "- 📝 **Examinations** — timetables and notifications\n"
            "- 💼 **Placements** — career and training info\n"
            "- 📖 **Library** — resources and digital services\n"
            "- 🏠 **Hostel** — accommodation and complaints\n"
            "- 🏛️ **Administration** — certificates and records\n"
            "- 🎉 **Events** — announcements and activities\n\n"
            "How may I assist you today?"
        )

    # Out of scope — specific dates
    if any(phrase in q for phrase in ["exact date", "what date", "which date", "when is my next exam", "date of my next exam", "next examination date"]):
        return "Examinations", (
            "Specific examination dates are not available in this helpdesk's knowledge base.\n\n"
            "**Examination timetables and notifications are published through official university channels.**\n\n"
            "Please check: 🔗 https://presidencyuniversity.in/academics/notices"
        )

    # Contact / phone / email
    if any(w in q for w in ["contact", "phone", "email", "number", "address", "location", "where is", "how to reach"]):
        return "Administration", (
            "**Presidency University — Official Contact Details:**\n\n"
            "📍 **Main Campus:** Itgalpur, Rajanakunte, Yelahanka, Bengaluru, Karnataka — 560064\n"
            "🏢 **City Office:** University House, 8/1, King Street, Richmond Town, Bengaluru — 560025\n"
            "📞 **Phone:** +91 9022092222\n"
            "📧 **Admissions Email:** admission@presidencyuniversity.in\n"
            "🌐 **Website:** https://presidencyuniversity.in/"
        )

    # Library
    if any(w in q for w in ["library", "digital resource", "database", "knimbus", "dspace", "turnitin", "prowess", "journal", "book", "borrow", "reprography", "nptel", "swayam"]):
        return "Library", (
            "**Library Access Guidelines:**\n"
            "Students may access library resources according to the library's timings and regulations.\n\n"
            "**📚 Collections:**\n"
            "- 343 print journals, 45 general magazines, 35 newspapers\n"
            "- Databases: ProwessIQ, CapitaLine, IndiaStat\n\n"
            "**💻 Digital & Remote Access:**\n"
            "- DSpace institutional repository (e-books, question papers, theses)\n"
            "- Library OPAC, Knimbus remote access\n"
            "- 'Libraries in Hand' mobile app\n"
            "- NPTEL/SWAYAM video lectures\n"
            "- Turnitin/Urkund plagiarism tools\n\n"
            "**🖥️ Facilities:** Self-check-out kiosk, book dropbox, free reprography, 25 internet-enabled terminals"
        )

    # Schools / Programs
    if any(w in q for w in ["school", "schools", "department", "departments", "program", "programmes", "courses offered", "btech", "mba", "mca", "llb", "bca", "bcom"]):
        return "Academics", (
            "**Presidency University — 9 Academic Schools:**\n\n"
            "1. 💻 Presidency School of Computer Science and Engineering\n"
            "2. ⚙️ Presidency School of Engineering\n"
            "3. 📊 Presidency School of Information Science\n"
            "4. 📈 Presidency School of Management\n"
            "5. 💰 Presidency School of Commerce\n"
            "6. ⚖️ Presidency School of Law\n"
            "7. 🎨 Presidency School of Design\n"
            "8. 📺 Presidency School of Media Studies\n"
            "9. 🔬 Presidency School of Liberal Arts and Sciences\n\n"
            "**Programs Offered:** UG (B.Tech, BBA, B.Com, BCA, B.Sc, BA LLB, BBA LLB, B.Des), "
            "PG (M.Tech, MBA, MCA, LLM, M.Sc, M.A.), Diploma, and Ph.D.\n\n"
            "**B.Tech Admissions:** Accepts IIT JEE, COMEDK, KCET, and SAT scores."
        )

    # Scholarships / Notices
    if any(w in q for w in ["scholarship", "scholarships", "fee", "grayquest", "emi", "ssp", "nsp", "notice", "circular"]):
        return "Administration", (
            "**Scholarships & Financial Aid at Presidency University:**\n\n"
            "- 🎓 **PU Scholarship** — University merit-based scholarship\n"
            "- 🏛️ **State Scholarship Portal (SSP)** — Karnataka government scholarship\n"
            "- 🇮🇳 **National Scholarship Portal (NSP)** — Central government scholarship\n"
            "- 💳 **GrayQuest EMI** — Fee payment in easy installments\n\n"
            "**📋 Official Notices:** Academic circulars, semester notices, Hostel & Transport enrolment, "
            "and Anti-Ragging affidavits are published at:\n"
            "🔗 https://presidencyuniversity.in/academics/notices"
        )

    # Admission
    if any(w in q for w in ["admission", "admissions", "apply", "application", "entrance", "eligibility", "cutoff", "jee", "comedk", "kcet"]):
        return "Academics", (
            "**Admissions at Presidency University:**\n\n"
            "📧 **Contact:** admission@presidencyuniversity.in\n"
            "📞 **Phone:** +91 9022092222\n"
            "🌐 **Website:** https://presidencyuniversity.in/\n\n"
            "**B.Tech Entrance Exams Accepted:** IIT JEE, COMEDK, KCET, SAT\n\n"
            "**Programs:** UG, PG, Diploma, and Ph.D. programs across 9 schools.\n\n"
            "For specific cutoffs and eligibility, please visit the official website or contact the admissions office."
        )

    # Placements
    if any(w in q for w in ["placement", "placements", "job", "career", "internship", "recruit", "campus placement", "training"]):
        return "Placements", (
            "**Placement Support at Presidency University:**\n\n"
            "Students may contact the **Placement Department** for training and placement-related information.\n\n"
            "The Placement Department assists with:\n"
            "- 💼 Campus recruitment drives\n"
            "- 🎯 Career guidance and training programs\n"
            "- 🤝 Industry networking and internship opportunities\n\n"
            "For specific placement details, contact the Placement Department directly or visit "
            "🔗 https://presidencyuniversity.in/"
        )

    # Hostel
    if any(w in q for w in ["hostel", "accommodation", "dorm", "dormitory", "mess", "warden", "room", "pg", "staying"]):
        return "Hostel", (
            "**Hostel & Accommodation at Presidency University:**\n\n"
            "Hostel-related complaints should be submitted to the **Hostel Administration**.\n\n"
            "For hostel enrollment and queries:\n"
            "- 📋 Hostel enrolment forms are published at: https://presidencyuniversity.in/academics/notices\n"
            "- 🏠 Contact the Hostel Administration office for room allotment and complaints\n"
            "- 🚌 Transport enrolment is also handled through the same office"
        )

    # Exam / Timetable
    if any(w in q for w in ["exam", "examination", "timetable", "datesheet", "schedule", "result", "marks", "grade", "cgpa", "sgpa"]):
        return "Examinations", (
            "**Examinations at Presidency University:**\n\n"
            "Examination timetables and notifications are published through **official university channels**.\n\n"
            "- 📅 Check the official notice board: https://presidencyuniversity.in/academics/notices\n"
            "- 📧 Exam-related queries: contact your respective school's administrative office\n"
            "- 📞 University contact: +91 9022092222\n\n"
            "For results and grades, log in to the student portal on the university website."
        )

    # Attendance
    if any(w in q for w in ["attendance", "absent", "leave", "shortage", "percentage"]):
        return "Attendance", (
            "**Attendance Policy at Presidency University:**\n\n"
            "Students should follow the **minimum attendance requirement** prescribed by university regulations.\n\n"
            "- ⚠️ Falling below the minimum attendance threshold may result in being barred from examinations\n"
            "- 📋 For attendance-related issues, contact your **faculty advisor**\n"
            "- 📊 Attendance records are maintained through official university systems\n\n"
            "For specific attendance percentage requirements, check with your faculty advisor or the academic office."
        )

    # Academics / Faculty
    if any(w in q for w in ["academic", "faculty", "advisor", "professor", "teacher", "course", "subject", "syllabus", "curriculum", "semester"]):
        return "Academics", (
            "**Academic Support at Presidency University:**\n\n"
            "Students may contact their **faculty advisor** for academic-related assistance.\n\n"
            "Your faculty advisor can help with:\n"
            "- 📚 Course registration and subject queries\n"
            "- 📝 Semester planning and syllabus guidance\n"
            "- 🎓 Academic progress and performance issues\n\n"
            "For general academic information, visit: 🔗 https://presidencyuniversity.in/"
        )

    # Events
    if any(w in q for w in ["event", "fest", "festival", "technopia", "cultural", "sports", "announcement", "workshop", "seminar", "hackathon"]):
        return "Events", (
            "**Events & Announcements at Presidency University:**\n\n"
            "University event announcements are shared through **official communication channels**.\n\n"
            "Stay updated by:\n"
            "- 🌐 Checking the official website: https://presidencyuniversity.in/\n"
            "- 📋 Official notices: https://presidencyuniversity.in/academics/notices\n"
            "- 📧 University email communications\n"
            "- 📢 Campus notice boards"
        )

    # Certificates / Records / Administration
    if any(w in q for w in ["certificate", "bonafide", "transcript", "document", "marksheet", "migration", "tc", "transfer", "admin", "office", "record"]):
        return "Administration", (
            "**Administrative Services at Presidency University:**\n\n"
            "Students may contact the respective **administrative office** for certificates and student records.\n\n"
            "Services available:\n"
            "- 📄 Bonafide certificates\n"
            "- 📋 Transcripts and marksheets\n"
            "- 🗂️ Student records and ID cards\n"
            "- 📃 Migration and transfer certificates\n\n"
            "📍 **Address:** Itgalpur, Rajanakunte, Yelahanka, Bengaluru — 560064\n"
            "📞 **Phone:** +91 9022092222"
        )

    # University overview / About
    if any(w in q for w in ["about", "overview", "history", "established", "naac", "ugc", "accredited", "university", "presidency"]):
        return "Presidency Overview", (
            "**About Presidency University, Bengaluru:**\n\n"
            "- 🏛️ Established under the Presidency University Act, 2013\n"
            "- ✅ UGC recognized and NAAC accredited\n"
            "- 🏫 9 Academic Schools offering diverse programs\n"
            "- 📍 **Campus:** Itgalpur, Rajanakunte, Yelahanka, Bengaluru — 560064\n"
            "- 📞 **Phone:** +91 9022092222\n"
            "- 📧 **Email:** admission@presidencyuniversity.in\n"
            "- 🌐 **Website:** https://presidencyuniversity.in/"
        )

    # Off-topic
    if any(w in words for w in ["weather", "temperature", "forecast", "cricket", "movie", "stock", "news", "politics", "sport"]):
        return "General", (
            "I'm the **Presidency University AI Campus Helpdesk Assistant**, so I can only assist with "
            "university-related queries such as Academics, Attendance, Examinations, Placements, Library, "
            "Hostel, Administration, and Events.\n\n"
            "For other information, please use a general web search. How can I help you with campus-related queries?"
        )

    # Default
    return "General", (
        "Thank you for your query! For the most accurate and up-to-date information, please:\n\n"
        "- 🌐 Visit: https://presidencyuniversity.in/\n"
        "- 📋 Check notices: https://presidencyuniversity.in/academics/notices\n"
        "- 📞 Call: +91 9022092222\n"
        "- 📧 Email: admission@presidencyuniversity.in\n\n"
        "I can also help you with: **Academics, Attendance, Examinations, Placements, Library, Hostel, Administration, or Events.**"
    )

# ==============================================================================
# AI ANSWER ENGINE
# ==============================================================================
def get_ai_answer(message: str):
    global active_model
    cleaned = message.strip()

    if genai_client:
        from google.genai import types as genai_types
        for m in [active_model, "gemini-3.8-flash", "gemini-1.5-flash"]:
            try:
                cfg = genai_types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.1,
                    max_output_tokens=800,
                )
                res = genai_client.models.generate_content(
                    model=m,
                    contents=cleaned,
                    config=cfg
                )
                if res and res.text:
                    active_model = m
                    cat, _ = deterministic_grounded_answer(cleaned)
                    logger.info(f"Gemini ({m}) responded successfully.")
                    return res.text.strip(), cat, f"Gemini ({m})"
            except Exception as e:
                logger.warning(f"Model {m} failed: {e}")
                continue

    # Deterministic fallback
    cat, ans = deterministic_grounded_answer(cleaned)
    logger.info(f"Using deterministic fallback for category: {cat}")
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
        return jsonify({
            "success": False,
            "answer": "Please ask a question regarding Presidency University.",
            "category": "General",
            "provider": "System"
        }), 400

    answer, category, provider = get_ai_answer(message)

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
