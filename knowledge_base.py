"""
CampusCompass AI - Authoritative University Knowledge Base
Strictly grounded in verified university information.
Never invents dates, fees, percentages, policies, phone numbers, or emails.
"""

UNIVERSITY_KNOWLEDGE_BASE = {
    "ACADEMICS": "Students may contact their faculty advisor for academic-related assistance.",
    "ATTENDANCE": "Students should follow the minimum attendance requirement prescribed by university regulations.",
    "EXAMINATIONS": "Examination timetables and notifications are published through official university channels.",
    "PLACEMENTS": "Students may contact the Placement Department for training and placement-related information.",
    "LIBRARY": "Students may access library resources according to the library's timings and regulations.",
    "HOSTEL": "Hostel-related complaints should be submitted to the Hostel Administration.",
    "ADMINISTRATION": "Students may contact the respective administrative office for certificates and student records.",
    "EVENTS": "University event announcements are shared through official communication channels."
}

CATEGORIES_META = [
    {
        "id": "academics",
        "name": "Academics",
        "description": "Faculty advisor guidance and academic assistance.",
        "icon": "bi-mortarboard-fill",
        "color": "lavender",
        "sample_question": "Whom should I contact for academic problems?"
    },
    {
        "id": "attendance",
        "name": "Attendance",
        "description": "Attendance regulations and policy guidance.",
        "icon": "bi-calendar-check-fill",
        "color": "mint",
        "sample_question": "What is the attendance requirement?"
    },
    {
        "id": "examinations",
        "name": "Examinations",
        "description": "Timetables, schedule notifications and channels.",
        "icon": "bi-journal-text",
        "color": "soft-blue",
        "sample_question": "Where can I find the examination timetable?"
    },
    {
        "id": "placements",
        "name": "Placements",
        "description": "Training and placement-related guidance.",
        "icon": "bi-briefcase-fill",
        "color": "lime",
        "sample_question": "Whom should I contact for placement training?"
    },
    {
        "id": "library",
        "name": "Library",
        "description": "Library resources, access and regulations.",
        "icon": "bi-book-half",
        "color": "amber",
        "sample_question": "What are the library timings?"
    },
    {
        "id": "hostel",
        "name": "Hostel",
        "description": "Hostel support, grievance and administration.",
        "icon": "bi-building-fill-check",
        "color": "coral",
        "sample_question": "How can I raise a hostel complaint?"
    },
    {
        "id": "administration",
        "name": "Administration",
        "description": "Certificates, student records and official paperwork.",
        "icon": "bi-folder2-open",
        "color": "soft-pink",
        "sample_question": "How do I get my student certificates?"
    },
    {
        "id": "events",
        "name": "Events",
        "description": "University announcements and official channels.",
        "icon": "bi-megaphone-fill",
        "color": "teal",
        "sample_question": "Where are university event announcements posted?"
    }
]

SYSTEM_PROMPT = """You are CampusCompass AI, a helpful university campus assistant. Answer student questions using ONLY the supplied university knowledge base. Understand natural language, paraphrased questions and contextual follow-up questions. Identify the appropriate category and generate clear, concise and friendly responses. Never invent university information, dates, fees, policies, contact information or statistics. If information is missing, explicitly state that it is unavailable in the supplied information and suggest the relevant official university channel only when supported by the knowledge base.

AUTHORITATIVE UNIVERSITY KNOWLEDGE BASE:
1. ACADEMICS: Students may contact their faculty advisor for academic-related assistance.
2. ATTENDANCE: Students should follow the minimum attendance requirement prescribed by university regulations.
3. EXAMINATIONS: Examination timetables and notifications are published through official university channels.
4. PLACEMENTS: Students may contact the Placement Department for training and placement-related information.
5. LIBRARY: Students may access library resources according to the library's timings and regulations.
6. HOSTEL: Hostel-related complaints should be submitted to the Hostel Administration.
7. ADMINISTRATION: Students may contact the respective administrative office for certificates and student records.
8. EVENTS: University event announcements are shared through official communication channels.

GROUNDING RULES:
- Never invent specific examination dates, timings, or schedules. State that specific dates are unavailable in the supplied information, and direct students to official university channels.
- Never invent specific attendance percentages (e.g. 75%, 80%). State that students should follow the minimum attendance requirement prescribed by university regulations.
- Never invent tuition or exam fees, hostel rent, or placement statistics/salary figures. State that fee and placement statistic details are unavailable in the supplied information.
- Never invent phone numbers, email addresses, or room numbers. Direct students to the respective office (Faculty Advisor, Placement Department, Hostel Administration, Administrative Office).
- Never invent exact library opening/closing hours or hostel curfew rules.
- If a question asks about topics outside the university campus scope (e.g., weather, global news, general chat), politely state that it is outside the supplied campus knowledge base.
- For friendly greetings (hello, hi, good morning), respond warmly and introduce your capabilities as CampusCompass AI.
"""

def classify_and_retrieve(query: str):
    """
    Deterministically identifies intent and retrieves grounded response
    for fallback or validation.
    """
    q = query.lower().strip()
    
    # Greetings
    if any(g in q for g in ["hello", "hi ", "hey", "how are you", "good morning", "good evening", "good afternoon"]) and len(q) < 30:
        return {
            "category": "General",
            "answer": "Hello! Welcome to CampusCompass AI. I'm your intelligent campus assistant. I can guide you with academics, attendance, examinations, placements, library, hostel, administration, and university events. What would you like to know today?",
            "grounded": True
        }
    
    # Specific Unavailability Checkers (mandatory test cases)
    # TC05: Exam dates
    if any(w in q for w in ["exact date", "what date", "which date", "when is my next exam", "date of my next exam", "exam date"]):
        return {
            "category": "Examinations",
            "answer": "The exact examination date is unavailable in the supplied information. Examination timetables and notifications are published through official university channels. Please refer to your university's official notification portal or notice board for the published schedule.",
            "grounded": True
        }
    
    # TC06: Library timings
    if any(w in q for w in ["library timing", "library timings", "library open", "library close", "hours of library", "time does the library"]):
        return {
            "category": "Library",
            "answer": "The exact library timings are unavailable in the supplied information. According to university guidelines, students may access library resources according to the library's timings and regulations. Please check the library entrance notice board or the official university portal for exact operational hours.",
            "grounded": True
        }
        
    # TC07: Fee structure
    if any(w in q for w in ["fee", "fees", "tuition", "cost", "hostel rent"]):
        return {
            "category": "Administration",
            "answer": "University fee structure details are unavailable in the supplied information. For official fee structures and payment guidelines, please contact the respective administrative office or consult official university circulars.",
            "grounded": True
        }
        
    # TC10: Weather or out-of-scope
    if any(w in q for w in ["weather", "temperature", "rain", "forecast", "stock", "cricket", "who won", "movie"]):
        return {
            "category": "General",
            "answer": "This inquiry is outside the supplied campus knowledge base. As CampusCompass AI, I provide guidance strictly regarding university academics, attendance, examinations, placements, library, hostel, administration, and events.",
            "grounded": True
        }

    # TC09: Administration (check records/certificates BEFORE academics so 'academic records' matches Administration)
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

    # TC01: Academics (Faculty Advisor)
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

    # General campus query fallback
    return {
        "category": "General",
        "answer": "I do not have specific details for this query in the supplied university knowledge base. I can assist you with verified information regarding academics, attendance, examinations, placements, library, hostel, administration, and university events. Please contact the relevant administrative office or consult official university channels for further assistance.",
        "grounded": True
    }
