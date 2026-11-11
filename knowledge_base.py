"""
Presidency University - Authoritative Knowledge Base
Dual-Tier Grounded Knowledge System:
Tier 1: 8 Mandatory TECHNOPIA 2.0 University Campus Rules
Tier 2: Verified presidencyuniversity.in Overview
Strict refusal to invent dates, fees, phone numbers, or unverified data.
"""

DUAL_TIER_SYSTEM_PROMPT = """You are the official Presidency University AI Campus Assistant (Presidency University — AI Campus Helpdesk).
Your mission is to provide helpful, accurate, concise, and strictly grounded guidance to students, faculty, and visitors.

TIER 1 — THE 8 MANDATORY TECHNOPIA 2.0 UNIVERSITY CAMPUS RULES:
1. ACADEMICS: Students may contact their faculty advisor for academic-related assistance.
2. ATTENDANCE: Students should follow the minimum attendance requirement prescribed by university regulations.
3. EXAMINATIONS: Examination timetables and notifications are published through official university channels.
4. PLACEMENTS: Students may contact the Placement Department for training and placement-related information.
5. LIBRARY: Students may access library resources according to the library's timings and regulations.
6. HOSTEL: Hostel-related complaints should be submitted to the Hostel Administration.
7. ADMINISTRATION: Students may contact the respective administrative office for certificates and student records.
8. EVENTS: University event announcements are shared through official communication channels.

TIER 2 — VERIFIED PRESIDENCY UNIVERSITY (presidencyuniversity.in) OVERVIEW:
- Institution: Presidency University, Bengaluru (Established under Karnataka Act No. 41 of 2013).
- Campus Location: Itgalpur, Rajanakunte, Yelahanka, Bengaluru, Karnataka 560064.
- Core Schools:
  * School of Engineering (SOE)
  * School of Management (SOM)
  * School of Law (SOL)
  * School of Design (SOD)
  * School of Computer Science & Information Technology (SOCSIT)
  * School of Commerce (SOC)
- Campus Features: Dedicated academic blocks, advanced engineering laboratories, expansive central library, on-campus student residences (hostels), sports arenas, cafeteria, and placement department.

STRICT GROUNDING & REFUSAL CONSTRAINTS:
- NEVER invent or guess examination dates, schedules, or hall tickets. State that specific dates are unavailable in the supplied information, and direct students to official university channels.
- NEVER invent tuition, exam, or hostel fee amounts. State that exact fee details are unavailable in the supplied information and direct students to the administrative office.
- NEVER invent attendance percentages (e.g. 75%, 85%). Reiterate that students should follow the minimum attendance requirement prescribed by university regulations.
- NEVER invent phone numbers, email addresses, or office room numbers.
- If a question is outside Presidency University / campus life (e.g. weather, general knowledge), politely state that it is outside the supplied campus knowledge base.
- Keep answers concise, factual, and friendly (maximum 2-3 sentences).
"""

CATEGORIES_META = [
    {
        "id": "academics",
        "name": "Academics",
        "description": "Faculty advisor guidance & academic support.",
        "icon": "bi-mortarboard-fill",
        "sample_question": "Whom should I contact for academic problems?"
    },
    {
        "id": "attendance",
        "name": "Attendance",
        "description": "Prescribed attendance rules & regulations.",
        "icon": "bi-calendar-check-fill",
        "sample_question": "What is the attendance requirement?"
    },
    {
        "id": "examinations",
        "name": "Examinations",
        "description": "Official timetables & notification channels.",
        "icon": "bi-journal-text",
        "sample_question": "Where can I find the examination timetable?"
    },
    {
        "id": "placements",
        "name": "Placements",
        "description": "Placement Department training & drives.",
        "icon": "bi-briefcase-fill",
        "sample_question": "Whom should I contact for placement training?"
    },
    {
        "id": "library",
        "name": "Library",
        "description": "Resource access, timings & rules.",
        "icon": "bi-book-half",
        "sample_question": "What are the library timings?"
    },
    {
        "id": "hostel",
        "name": "Hostel",
        "description": "Hostel Administration & grievances.",
        "icon": "bi-building-fill-check",
        "sample_question": "How can I raise a hostel complaint?"
    },
    {
        "id": "administration",
        "name": "Administration",
        "description": "Certificates, records & paperwork.",
        "icon": "bi-folder2-open",
        "sample_question": "How do I get my student certificates?"
    },
    {
        "id": "events",
        "name": "Events",
        "description": "Announcements & official feeds.",
        "icon": "bi-megaphone-fill",
        "sample_question": "Where are university event announcements posted?"
    }
]

# High-speed deterministic fallback engine (instant 1ms response)
def classify_and_retrieve(query: str):
    q = query.lower().strip()
    
    # Greetings
    if any(g in q for g in ["hello", "hi ", "hey", "how are you", "good morning", "good evening", "good afternoon"]) and len(q) < 30:
        return {
            "category": "General",
            "answer": "Hello! Welcome to the Presidency University AI Campus Helpdesk. I can guide you regarding academics, attendance, examinations, placements, library, hostel, administration, and university schools. What would you like to know today?",
            "grounded": True
        }

    # Overview of Presidency University
    if any(w in q for w in ["about presidency", "where is presidency", "location", "schools", "overview", "what is presidency university"]):
        return {
            "category": "Presidency Overview",
            "answer": "Presidency University, Bengaluru (established under Karnataka Act No. 41 of 2013) is located at Itgalpur, Rajanakunte, Yelahanka, Bengaluru. The university hosts core schools including Engineering (SOE), Management (SOM), Law (SOL), Design (SOD), Computer Science & IT (SOCSIT), and Commerce (SOC).",
            "grounded": True
        }

    # TC05: Exam dates
    if any(w in q for w in ["exact date", "what date", "which date", "when is my next exam", "date of my next exam", "exam date"]):
        return {
            "category": "Examinations",
            "answer": "The exact examination date is unavailable in the supplied information. Examination timetables and notifications are published through official university channels.",
            "grounded": True
        }
    
    # TC06: Library timings
    if any(w in q for w in ["library timing", "library timings", "library open", "library close", "hours of library", "time does the library"]):
        return {
            "category": "Library",
            "answer": "Specific library timings are unavailable in the supplied information. Students may access library resources according to the library's timings and regulations.",
            "grounded": True
        }
        
    # TC07: Fee structure
    if any(w in q for w in ["fee", "fees", "tuition", "cost", "hostel rent"]):
        return {
            "category": "Administration",
            "answer": "University fee structure details are unavailable in the supplied information. For official fee structures, please contact the respective administrative office.",
            "grounded": True
        }
        
    # TC10: Out of Scope (use word boundaries so 'rain' does not match 'training')
    words = set(q.split())
    if any(w in words for w in ["weather", "temperature", "rain", "raining", "forecast", "cricket", "movie", "stock"]):
        return {
            "category": "General",
            "answer": "This inquiry is outside the supplied campus knowledge base. As Presidency University AI Helpdesk, I provide guidance strictly regarding university academics, regulations, and campus facilities.",
            "grounded": True
        }

    # TC09: Administration (Certificates & Records)
    if any(w in q for w in ["certificate", "certificates", "record", "records", "transcript", "transcripts", "document", "marksheet", "admin office", "bonafide"]):
        return {
            "category": "Administration",
            "answer": "Students may contact the respective administrative office for certificates and student records.",
            "grounded": True
        }

    # TC03: Placements & Training
    if any(w in q for w in ["placement", "placements", "job", "internship", "career", "training", "recruit", "campus interview", "resume"]):
        return {
            "category": "Placements",
            "answer": "Students may contact the Placement Department for training and placement-related information.",
            "grounded": True
        }

    # TC04: Hostel
    if any(w in q for w in ["hostel", "room", "mess", "dorm", "warden", "roommate", "accommodation"]):
        return {
            "category": "Hostel",
            "answer": "Hostel-related complaints should be submitted to the Hostel Administration.",
            "grounded": True
        }

    # TC02: Examinations
    if any(w in q for w in ["exam", "examination", "timetable", "test schedule", "datesheet", "hall ticket"]):
        return {
            "category": "Examinations",
            "answer": "Examination timetables and notifications are published through official university channels.",
            "grounded": True
        }

    # TC01: Academics
    if any(w in q for w in ["academic", "faculty", "advisor", "professor", "course", "subject", "syllabus", "mentor", "failing"]):
        return {
            "category": "Academics",
            "answer": "Students may contact their faculty advisor for academic-related assistance.",
            "grounded": True
        }

    # Attendance
    if any(w in q for w in ["attendance", "leave", "absent", "minimum attendance", "shortage"]):
        return {
            "category": "Attendance",
            "answer": "Students should follow the minimum attendance requirement prescribed by university regulations.",
            "grounded": True
        }

    # Library
    if any(w in q for w in ["library", "book", "journal", "reading room", "borrow"]):
        return {
            "category": "Library",
            "answer": "Students may access library resources according to the library's timings and regulations.",
            "grounded": True
        }

    # Events
    if any(w in q for w in ["event", "fest", "cultural", "sports", "seminar", "workshop", "announcement"]):
        return {
            "category": "Events",
            "answer": "University event announcements are shared through official communication channels.",
            "grounded": True
        }

    return {
        "category": "General",
        "answer": "I do not have specific details for this query in the supplied university knowledge base. Please contact the relevant administrative office or consult official university channels for verified guidance.",
        "grounded": True
    }
