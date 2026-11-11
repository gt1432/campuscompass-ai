# CampusCompass AI

> **"Your Campus. One Smart Assistant."**  
> *Your intelligent guide to university life.*

CampusCompass AI is a production-grade, full-stack university helpdesk assistant engineered with **Python Flask**, **Google Gemini 3.8 Flash**, and a responsive modern editorial frontend. It provides verified, authoritative, and strictly grounded guidance across 8 core university domains.

---

## 🌟 Key Features

1. **AI-Powered Assistance**
   - Direct integration with Google's latest **Gemini 3.8 Flash** via the official `google-genai` Python SDK.
   - Low-latency contextual understanding with strict temperature tuning to guarantee grounding.

2. **Authoritative University Grounding (Zero Hallucination)**
   - Strict boundaries enforced by system prompt engineering and deterministic intent verification.
   - Responds strictly using verified campus knowledge:
     - **Academics**: Faculty advisor guidance.
     - **Attendance**: Official university regulations.
     - **Examinations**: Official publication channels.
     - **Placements**: Training & Placement Department.
     - **Library**: Official timings & regulations.
     - **Hostel**: Hostel Administration.
     - **Administration**: Respective administrative office for certificates & records.
     - **Events**: Official university communication channels.
   - Explicitly discloses when exact dates, fees, or operational hours are unavailable in supplied records.

3. **High-Resilience Dual-Mode Architecture**
   - Primary: Real-time Google Gemini 3.8 Flash inference.
   - Fallback: Clearly labeled, deterministic knowledge-base retrieval engine when offline, credentials absent, or API quotas exceeded.

4. **Premium UI/UX Design System**
   - Minimal editorial typography with **Inter** and **JetBrains Mono**.
   - Warm cream background (`#FAF8F5`) with pastel lavender, mint, lime, coral, and soft blue accents.
   - 8 interactive, animated category cards with instant one-touch question firing.
   - Dynamic animated AI mascot with floating status badges.
   - Live system health monitoring badge linked to `/api/health`.

5. **Conversational Helpdesk Interface**
   - Student & Assistant chat bubbles with timestamps and category chips.
   - Provider transparency badge (`Gemini 3.8 Flash` vs `KnowledgeBase`).
   - One-click copy response with toast notifications.
   - Helpful / Not Helpful feedback recording.
   - Auto-scroll, typing indicator, auto-expanding textarea.
   - Persistent session storage in `localStorage` and optional MongoDB Atlas integration.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons |
| **Backend** | Python 3.12, Flask 3.0+ |
| **AI / LLM** | Google Gemini API (Official `google-genai` SDK, `gemini-3.8-flash`) |
| **Database** | MongoDB Atlas with PyMongo (Optional, graceful in-memory fallback) |
| **WSGI Server** | Gunicorn |
| **Deployment** | Render Web Service (`render.yaml`) |

---

## 📁 Project Structure

```text
campuscompass-ai/
├── app.py                 # Flask server & REST API routes (/api/chat, /api/health, etc.)
├── config.py              # Centralized configuration & environment loader
├── ai_service.py          # Google Gemini 3.8 Flash integration & prompt grounding
├── knowledge_base.py      # Authoritative facts, category metadata & fallback engine
├── database.py            # MongoDB Atlas persistence with in-memory fallback
├── test_suite.py          # Automated test suite verifying TC01–TC10 & multi-turn flows
├── requirements.txt       # Production dependencies
├── render.yaml            # Render Blueprint deployment specification
├── .env.example           # Template for environment variables
├── .gitignore             # Secrets & cache exclusion
├── templates/
│   └── index.html         # Editorial landing page & embedded chat interface
└── static/
    ├── css/
    │   └── style.css      # Custom styling, animations & pastel theme
    └── js/
        └── app.js         # Chat client, health polling & interactions
```

---

## 🚀 Quick Start & Local Setup

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Clone the Repository
```bash
git clone https://github.com/<your-username>/campuscompass-ai.git
cd campuscompass-ai
```

### 3. Create a Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Populate `.env` with your credentials:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.8-flash
MONGODB_URI=your_mongodb_connection_string_optional
FLASK_SECRET_KEY=generate_a_random_key_here
PORT=5000
HOST=0.0.0.0
```

### 6. Run the Application
```bash
python app.py
```
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 🧪 Automated Test Suite (Mandatory Test Cases)

Run the automated verification suite:
```bash
python test_suite.py
```

### Verified Test Results

| ID | Test Question | Expected Output | Status |
|---|---|---|---|
| **TC01** | Whom should I contact for academic problems? | Faculty advisor | **PASSED** |
| **TC02** | Where can I find the examination timetable? | Official university channels | **PASSED** |
| **TC03** | Whom should I contact for placement training? | Placement Department | **PASSED** |
| **TC04** | How can I raise a hostel complaint? | Hostel Administration | **PASSED** |
| **TC05** | What is the exact date of my next examination? | Date unavailable in supplied information | **PASSED** |
| **TC06** | What are the library timings? | Exact timings unavailable | **PASSED** |
| **TC07** | What is the university fee structure? | Information unavailable | **PASSED** |
| **TC08** | Hello, how are you? | Friendly greeting & assistant introduction | **PASSED** |
| **TC09** | I need my academic records and certificates. | Respective administrative office | **PASSED** |
| **TC10** | What is the weather today? | Outside supplied campus knowledge base | **PASSED** |
| **P01** | Paraphrased queries (e.g., room water leaks, failing subjects) | Contextually grounded answers | **PASSED** |
| **F01** | Multi-turn contextual follow-ups (Resume/training) | Preserved domain context | **PASSED** |

---

## 🌐 Deployment to Render

The repository includes a ready-to-deploy `render.yaml` configuration.

### Render Deployment Steps:
1. Push this repository to **GitHub**.
2. Log in to [Render Dashboard](https://dashboard.render.com).
3. Click **New +** → **Blueprint** and select your `campuscompass-ai` repository (or **New Web Service**).
4. Configure settings:
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Under **Environment Variables**, add:
   - `GEMINI_API_KEY`: *(Your Google Gemini API Key)*
   - `GEMINI_MODEL`: `gemini-3.8-flash`
   - `MONGODB_URI`: *(Optional MongoDB connection string)*
   - `FLASK_SECRET_KEY`: *(Any secure random string)*
6. Click **Deploy**. Render will build and launch CampusCompass AI with automatic SSL.

---

## 🛡️ Grounding & Security Principles
- **No Hallucination**: Strict prompts ensure the assistant never fabricates dates, contact numbers, or policies.
- **Credential Protection**: All API keys and database strings are isolated in `.env` and excluded via `.gitignore`.
- **Graceful Degradation**: If external APIs experience rate limiting or high load, CampusCompass AI automatically falls back to its deterministic knowledge base.

---

## 📄 License & Attribution
&copy; 2026 CampusCompass AI. Designed and engineered for university excellence.
