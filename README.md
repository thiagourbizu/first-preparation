# Cambridge B2 First (FCE) — Reading & Use of English Part 4 Trainer

Modern, responsive web platform designed for students preparing for the **Cambridge B2 First (FCE)** examination, specifically **Reading and Use of English Part 4 (Key Word Transformation)**.

Contains a curated database of **820 verified Cambridge practice tasks** extracted from official exam papers, Cambridge English trainers, Flo-Joe, and ESL Lounge.

---

## 🌟 Key Features

- **Zero-Friction Student Access**: Students enter their name once on their phone or computer. Device-level identification (`localStorage`) syncs their attempts and scores without the friction of remembering passwords.
- **Strict Cambridge Rule Compliance**:
  - Keyword must remain unchanged.
  - 2 to 5 words constraint strictly verified.
  - 100% exact match evaluation.
  - Built-in contraction tolerance (`didn't let him go` $\equiv$ `did not let him go`).
- **Official Exam Simulation**:
  - 6 random tasks (official Cambridge Part 4 format).
  - 10-minute countdown timer with visual progress bar.
  - Score breakdown out of 12 marks (Cambridge B2 Pass threshold: $\ge 8/12$ marks).
- **Practice Mode**:
  - Instant question-by-question check with full grammar explanations.
  - Real-time word counter (flags $< 2$ or $> 5$ words).
  - Dataset selector (filter by Book 0, Book 1, Book 2, Flo-Joe, ESL Lounge, or All).
- **Community Alternative Answer Suggestions**:
  - If a student's answer was marked wrong but is grammatically valid, they can submit an alternative with one click.
  - Teachers review and approve suggestions in the Admin Portal with one click, immediately adding them to the exercise's acceptable key.
- **Teacher / Admin Portal**:
  - Protected by a master passphrase.
  - Manage exercises (CRUD, lock verified Cambridge tasks).
  - Review student suggestions queue.
  - View student roster and score averages.
- **Modern Minimalist UI**:
  - Fast, thumb-friendly mobile layout.
  - Light mode and Dark mode toggle.

---

## 🏗️ Architecture & Security

- **Frontend**: Vue 3 (Composition API) + Vite + Tailwind CSS + Lucide Icons.
- **Backend**: FastAPI (Python 3.11+) + SQLModel + SQLite in **WAL (Write-Ahead Logging)** mode.
- **Deployment**: **Single unified container** (FastAPI serves both the API and the compiled Vue frontend) + optional **Cloudflare Tunnel (`cloudflared`)**.
- **Security**:
  - **Zero Open Router Ports**: Cloudflare Tunnel creates an encrypted outbound WebSocket connection. Your home IP address is completely shielded.
  - **SQL Injection Proof**: Parameterized SQL queries via SQLModel.
  - **Admin Isolation**: All management endpoints require `X-Admin-Password`.

---

## 🚀 Quick Start (Docker Deployment)

### 1. Configure Environment
```bash
cp .env.example .env
```
Edit `.env` to set your desired `ADMIN_PASSWORD` (and `CLOUDFLARE_TUNNEL_TOKEN` if exposing publicly).

### 2. Launch with Docker Compose
```bash
docker compose up -d --build
```
The application will boot at `http://localhost:8000`.

To stop the application at any time:
```bash
docker compose down
```

---

## 🛠️ Local Development (Without Docker)

### Backend
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate       # Windows
pip install -r requirements.txt
python scripts/seed.py          # Seeds the 820 exercises into fce.db
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev                    # Runs Vite dev server at http://localhost:3000 (proxies /api to 8000)
```

To build frontend for production:
```bash
npm run build
```

---

## 🧪 Running Automated Tests

```bash
cd backend
.\venv\Scripts\python tests/test_api.py
```
Validates engine contraction normalization, keyword enforcement, random draw, exam submission, scoring, and admin endpoints.
