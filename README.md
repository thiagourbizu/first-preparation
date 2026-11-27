# Cambridge B2 First (FCE) — Reading & Use of English Part 4 Trainer

Modern, responsive web platform designed for students preparing for the **Cambridge B2 First (FCE)** examination, specifically **Reading and Use of English Part 4 (Key Word Transformation)**.

Contains a curated database of **820 verified Cambridge practice tasks** extracted from official exam papers, Cambridge English trainers, Flo-Joe, and ESL Lounge.

🌐 **Live URL**: [https://thiagourbizu.github.io/first-preparation/](https://thiagourbizu.github.io/first-preparation/)

---

## 🌟 Key Features

- **Zero-Friction Student Access**: Students enter their name once on their phone or computer. Device-level identification (`localStorage`) syncs their attempts and scores without passwords.
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
  - Instant question-by-question check with grammar explanations.
  - Real-time word counter (flags $< 2$ or $> 5$ words).
  - Dataset selector (filter by Book 0, Book 1, Book 2, Flo-Joe, ESL Lounge, or All sources).
- **Local History & Progress**:
  - Track exam attempts, scores, and completion times saved directly in the browser.
- **Modern Minimalist UI**:
  - Nordic Rationalist aesthetic: clean, light-mode design with high typography hierarchy.
  - Fast, thumb-friendly mobile layout designed for smartphones, tablets, and desktops.

---

## 🏗️ Architecture & Deployment

This version is designed to run **100% client-side** and is hosted globally with **GitHub Pages**:

- **Frontend**: Vue 3 (Composition API) + Vite + Tailwind CSS + Lucide Icons.
- **Dataset**: Precompiled JSON bundle (`exercises.json`) containing all 820 Cambridge exercises for instant, offline-capable loading.
- **Grading Engine**: Fully client-side normalization engine (`services/grader.js`) implementing exact Cambridge evaluation rules.
- **Continuous Deployment**: Automated via **GitHub Actions** (`.github/workflows/deploy.yml`) on every push to the `main` branch.

> [!NOTE]
> **Need the legacy Docker + Cloudflare / Ngrok backend version?**
> The full-stack Python (FastAPI + SQLite WAL) and Docker container setup is preserved in the **`docker-deployment`** branch:
> ```bash
> git checkout docker-deployment
> ```

---

## 🚀 Quick Start (Local Development)

### 1. Install Dependencies
```bash
# At repository root
npm --prefix frontend install
```

### 2. Start Dev Server
```bash
npm run dev
```
Open your browser at `http://localhost:3000`.

### 3. Build for Production
```bash
npm run build
```
The compiled static assets are generated in `frontend/dist/`.

---

## 📦 Deploying to GitHub Pages

Deployment is automated with GitHub Actions:
1. Push your changes to the `main` branch.
2. In your GitHub repository: go to **Settings** $\rightarrow$ **Pages**.
3. Under **Build and deployment** $\rightarrow$ **Source**, select **GitHub Actions**.
4. The workflow will run automatically and publish the app at `https://thiagourbizu.github.io/first-preparation/`.
