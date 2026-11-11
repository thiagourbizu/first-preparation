---
type: constitution
title: first-preparation — Constitution
description: The non-negotiable principles every rsc-sdd phase obeys for the Cambridge B2 First Trainer.
tags: [sdd, constitution, fce, cambridge]
timestamp: 2026-11-07T15:30:00Z
topic: sdd
status: ratified
version: v1.0.0
---

# first-preparation — Constitution

> Version: v1.0.0 · Ratified: 2026-11-07 · Last amended: 2026-11-07
> The non-negotiable principles every rsc-sdd phase obeys. Stack mechanics live in
> `02-DOCS/wiki/stack/*`; this file ratifies the principles and links the detail.

## 1. Stack canon

1. **Primary runtimes & environments:** Python 3.11+ backend pinned in `backend/requirements.txt`; Node 22+ frontend pinned in `frontend/package.json`. Containerization pinned in `Dockerfile` (multi-stage build `node:22-alpine` $\rightarrow$ `python:3.11-slim`) and orchestrated via `docker-compose.yml`.
2. **Frameworks fixed:** FastAPI backend for REST APIs, SQLModel (SQLAlchemy + Pydantic) with SQLite database, and Vue 3 (Composition API with `<script setup>`) + Vite + Tailwind CSS for the client. Changing or swapping any of these frameworks requires a MAJOR amendment.
3. **Deployment architecture:** Single unified Docker container serving both the FastAPI backend and compiled Vue 3 static distribution (`frontend/dist`), paired with Cloudflare Zero Trust Tunnel (`cloudflare/cloudflared`) on protocol `http2`.

## 2. Quality bar

4. **Code cleanliness & formatting:** Python code must be clean, correctly typed, and syntax-valid. Frontend code must build cleanly via `npm run build` without unresolved module imports or compile warnings.
5. **Types & schema enforcement:** API payloads and database tables are strictly defined using SQLModel/Pydantic models (`backend/app/models.py`). Unvalidated arbitrary dictionaries are forbidden on public endpoints.
6. **Cambridge Grading Engine discipline:** Strict compliance with Cambridge B2 First Part 4 examination standards (`backend/app/engine.py`):
   - Constraint of 2 to 5 words (including keyword).
   - Keyword must remain unmodified (case-insensitive check, original characters preserved).
   - Exact half-mark splitting (2 points total: 1 mark per correct half).
   - Contraction tolerance (`didn't` == `did not`) and unicode/curly apostrophe normalization (`’` $\rightarrow$ `'`).
   - Line test coverage on engine grading logic must be $\ge 90\%$ before any release.

## 3. Conventions

7. **Directory layout & module boundaries:**
   - `backend/app/api/`: Modular routers (`practice.py`, `exam.py`, `suggestions.py`, `admin.py`).
   - `backend/app/engine.py`: Isolated Cambridge grading business logic.
   - `backend/data/seeds/`: JSON seed datasets (primary: `libro_que_usamos_en_clase.json`).
   - `frontend/src/views/`: Dedicated page views (`PracticeView.vue`, `ExamView.vue`, `HistoryView.vue`, `AdminView.vue`).
   - `frontend/src/components/`: Reusable interface elements (`Navbar.vue`).
8. **API design & error shapes:** JSON response envelopes with standardized HTTP status codes (200 OK, 400 Bad Request, 401 Unauthorized for admin access, 404 Not Found).
9. **Commit messages:** Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`, `chore:`).

## 4. Branching & shipping

10. **Delivery workflow:** Direct pushes to the default branch (`main`) as established during onboarding (`--workflow main`), gated by local verification before pushing.
11. **Git authorship is the human's:** All commits and PRs are strictly authored by the responsible human developer (`Thiago`). No `Co-Authored-By` AI tags, generated-by badges, or AI attribution footers. Enforced at the `ship` phase.

## 5. Security & privacy floor

12. **Secret discipline:** No credentials, API tokens, or secrets are ever committed to version control. Passwords (`ADMIN_PASSWORD`), session keys (`SECRET_KEY`), and tunnel tokens (`CLOUDFLARE_TUNNEL_TOKEN`) load exclusively from the root `.env` file (strictly gitignored). SQLite databases (`fce.db*`) are never tracked.
13. **Student privacy & zero-friction authentication:** Student accounts require no registration, emails, or passwords. Student identity is locally generated (UUID and chosen name in browser `localStorage`). Teacher/Admin features are protected by master passphrase authentication.
14. **Network isolation:** Public internet exposure is managed entirely through outbound Cloudflare Zero Trust Tunnels. No router ports (80/443/8000) are opened publicly on the local network.

## 6. UX & accessibility floor

15. **Design aesthetics & visual clarity:** Nordic Rationalist minimalist design system. Light theme only (night/dark mode is explicitly discarded). High-contrast typography (`Inter`, `Plus Jakarta Sans`, `JetBrains Mono`), calm neutral palettes (`bg-nordic-50`), and zero intrusive modals.
16. **Exam & practice ergonomics:**
   - Sentence transformation inputs have generous horizontal spacing (`mx-2`, `mr-2`, `ml-2`) preventing text from touching input borders.
   - Real-time client-side word counter validating the 2-5 word limit without server roundtrip delay.
   - Timed Exam mode displays all 6 tasks simultaneously on a single scrollable view with a sticky countdown timer (10:00).

## 7. Performance budgets

17. **Backend response budget:** p95 API response time $\le 100\text{ms}$ for practice exercise retrieval and evaluation. SQLite operates in WAL mode (`journal_mode=WAL`, `synchronous=NORMAL`) ensuring zero idle memory overhead and non-blocking concurrent reads.
18. **Client bundle budget:** Production frontend build $\le 300\text{kB}$ gzipped to ensure sub-second rendering on mobile connections.

## 8. Knowledge & decisions

19. **Decisions are logged:** Every significant architectural, data modeling, or grading decision is appended to `02-DOCS/wiki/sdd/decisions.md` with date, options evaluated, and rationale. The constitution is the foundational decision record.

---

## Definition of Done (the merge bar `verify` runs against)

A change ships only when ALL hold:

- [ ] Python syntax and formatting are clean; frontend builds cleanly with zero errors (`npm run build`).
- [ ] Type schemas (SQLModel/Pydantic) are respected across all modified endpoints.
- [ ] Cambridge grading engine rules (2-5 words, keyword intact, contraction handling) pass automated tests.
- [ ] Code follows project conventions (directory layout, views/components separation).
- [ ] Change lands on `main` authored exclusively by the human developer without AI attribution tags.
- [ ] No secrets, `.env` entries, or SQLite database files are committed to git.
- [ ] UI changes maintain the minimalist Nordic light theme, proper input spacing, and responsive layout.
- [ ] Significant decisions and seed dataset modifications are logged in `02-DOCS/wiki/sdd/decisions.md`.

---

## Amendment log (append-only)

| Date | Version | Change | Why |
|------|---------|--------|-----|
| 2026-11-07 | v1.0.0 | Ratified initial constitution. | Project baseline established: FCE Part 4 training platform, Docker unified container, Cloudflare tunnel routing, and Nordic minimalist UI. |
