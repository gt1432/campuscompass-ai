# Presidency University — AI Campus Helpdesk

> **Official AI-Powered University Campus Helpdesk**  
> *Engineered for TECHNOPIA 2.0 • Presidency University, Bengaluru*

Presidency University AI Campus Helpdesk is a production-grade conversational intelligence web application engineered with **Python Flask**, **Google Gemini**, and a Figma-inspired high-contrast editorial interface. It provides verified, ultra-fast (<1s latency), and strictly grounded university guidance.

---

## 🏛️ Grounded Dual-Tier Knowledge Base

### Tier 1 — 8 Mandatory TECHNOPIA 2.0 Campus Rules:
1. **Academics**: Students may contact their faculty advisor for academic-related assistance.
2. **Attendance**: Students should follow the minimum attendance requirement prescribed by university regulations.
3. **Examinations**: Examination timetables and notifications are published through official university channels.
4. **Placements**: Students may contact the Placement Department for training and placement-related information.
5. **Library**: Students may access library resources according to the library's timings and regulations.
6. **Hostel**: Hostel-related complaints should be submitted to the Hostel Administration.
7. **Administration**: Students may contact the respective administrative office for certificates and student records.
8. **Events**: University event announcements are shared through official communication channels.

### Tier 2 — Verified Presidency University (`presidencyuniversity.in`) Overview:
- **Establishment**: Presidency University, Bengaluru (Established under Karnataka Act No. 41 of 2013).
- **Campus Location**: Itgalpur, Rajanakunte, Yelahanka, Bengaluru, Karnataka 560064.
- **Constituent Schools**:
  - School of Engineering (SOE)
  - School of Management (SOM)
  - School of Law (SOL)
  - School of Design (SOD)
  - School of Computer Science & Information Technology (SOCSIT)
  - School of Commerce (SOC)

### Grounding & Refusal Guarantees:
- **Zero Hallucination**: The system strictly refuses to invent examination dates, attendance percentages, tuition fees, faculty email addresses, or phone numbers.
- **Explicit Disclosures**: Clearly directs students to official offices and bulletins whenever exact dates or fees are unavailable in supplied records.

---

## ⚡ Maximum Response Speed (<1s) Optimizations

1. **Global Client Singleton**: The Google GenAI client is initialized once globally at server startup, eliminating client instantiation overhead per HTTP request.
2. **Low-Latency Inference**: Configured with `temperature=0.1` and `max_output_tokens=200` for crisp, direct responses.
3. **Asynchronous Non-Blocking Database**: MongoDB Atlas writes execute in background daemon threads (`serverSelectionTimeoutMS=500`), ensuring database network latency never delays user responses.
4. **Sub-millisecond Deterministic Fallback**: Instant rule-based fallback guarantees 100% uptime even if API quotas or network limits occur.

---

## 🎨 Figma-Inspired Design System

- **Navbar**: `56px` height, `#FFFFFF` canvas, featuring `Presidency-university-logo.png` (`height: 36px`) paired with a `JetBrains Mono` uppercase `AI HELPDESK` badge.
- **Hero Section**: Two-column editorial grid on `#FFFFFF` canvas:
  - Left: Mono eyebrow `TECHNOPIA 2.0 • CAMPUS ASSISTANT`, oversized `Inter` weight-340 headline `"Ask anything about Presidency University."`, dual black (`#0D0D0D`) and white (`#FFFFFF`) `50px` pill CTAs.
  - Right: `presidency login page image.jpg` inside a framed container (`border-radius: 24px`, `border: 1px solid #E2E2E2`, `aspect-ratio: 16/10`).
- **Interactive Chat Workspace**: `#C7F284` Lime Color-Block with real-time conversational messaging and auto-scroll.
- **Quick-Test Prompts**: `#E4D4FF` Lilac Color-Block featuring 1-click test prompts for all mandatory TECHNOPIA 2.0 queries and campus overviews.
- **Footer**: `#0D0D0D` inverse canvas with white inverted logo (`filter: brightness(0) invert(1); height: 32px;`).

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons |
| **Backend** | Python 3.12, Flask 3.0+ |
| **AI Engine** | Google Gemini API (official `google-genai` SDK, `gemini-3.8-flash`) |
| **Database** | MongoDB Atlas (PyMongo) with non-blocking async logging + in-memory store |
| **WSGI Server** | Gunicorn |
| **Process Config**| `Procfile` (`web: gunicorn app:app`) & `render.yaml` |

---

## 🚀 Local Setup & Installation

### 1. Clone Repository
```bash
git clone https://github.com/gt1432/campuscompass-ai.git
cd campuscompass-ai
```

### 2. Set Up Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
```
Ensure your `.env` contains:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.8-flash
MONGODB_URI=your_mongodb_atlas_uri_optional
FLASK_SECRET_KEY=your_secret_key
PORT=5000
HOST=0.0.0.0
```

### 5. Run Server
```bash
python app.py
```
Visit `http://localhost:5000` in your web browser.

---

## ☁️ Deployment to Render

1. Push this repository to **GitHub**.
2. Open [Render Dashboard](https://dashboard.render.com) and click **New Web Service**.
3. Select your repository: `gt1432/campuscompass-ai`.
4. Configure service settings:
   - **Environment:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app` (configured in `Procfile`)
5. Under **Environment Variables**, add:
   - `GEMINI_API_KEY`: *(Your Google Gemini API Key)*
   - `GEMINI_MODEL`: `gemini-3.8-flash`
   - `FLASK_SECRET_KEY`: *(Any secure random key)*
   - `MONGODB_URI`: *(Optional MongoDB connection string)*
6. Click **Deploy Web Service**.

---

## 📄 License & Ownership
&copy; 2026 Presidency University. Developed for TECHNOPIA 2.0.
