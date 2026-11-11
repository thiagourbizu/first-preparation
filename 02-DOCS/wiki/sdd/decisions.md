# SDD Decisions Log

Every significant technical, architectural, or design decision is recorded here with date, alternatives considered, and rationale.

---

## [DEC-001] 2026-11-07 — Ratification of Initial Constitution (v1.0.0)

- **Context:** Project initialization of the Cambridge B2 First (FCE) Reading & Use of English Part 4 training web platform.
- **Decision:** Ratified `02-DOCS/wiki/sdd/constitution.md` at v1.0.0 covering the 8 foundational dimensions:
  1. Python 3.11+ / FastAPI + Vue 3 / Vite + SQLite (WAL mode).
  2. Strict Cambridge grading engine (2-5 word constraint, keyword intact, contraction normalization).
  3. Single-container Docker deployment + Cloudflare Tunnel (HTTP/2).
  4. Zero-friction student identity (`localStorage` UUID) + Admin master passphrase.
  5. Nordic Rationalist light-mode UI (no dark mode).
  6. Git authorship assigned exclusively to the human developer.
- **Options Considered:**
  - *Database:* MongoDB vs. PostgreSQL vs. SQLite $\rightarrow$ Selected SQLite with WAL mode for zero idle memory, simple file backup, and sufficient concurrency for class batches.
  - *Authentication:* Traditional user/password registration vs. zero-friction client identity $\rightarrow$ Selected zero-friction UUID/name in `localStorage` for students to eliminate onboarding friction, paired with admin passphrase.
  - *Deployment:* Multi-container (separate backend, Nginx, cloudflared) vs. Unified container $\rightarrow$ Selected unified multi-stage container + cloudflared tunnel for lightweight, single-click lifecycle management.
- **Outcome:** Constitution v1.0.0 is the active law of the repository.

---

## [DEC-002] 2026-11-07 — Configurable Dataset Source Filter in Timed Exam Mode

- **Context:** Students preparing for the exam need the flexibility to either practice under realistic mock conditions drawing from all combined sources or isolate the test to the specific classroom book ("Libro que usamos en clase") or other curated collections.
- **Decision:**
  - Added a reactive dataset selector to the Timed Exam idle start view.
  - The dropdown defaults to **"All sources"** (820 total exercises), immediately followed by **"Libro que usamos en clase"** (248 exercises), and then the external supplementary collections.
  - The backend `/api/exam/start` endpoint now enforces the `book` filter while sampling the 6 random questions.
  - The active exam sticky header and the results breakdown display the selected dataset badge, preserving the filter in the attempt record and student history.
- **Outcome:** Consistent ergonomic dataset selection across both Practice and Exam views without violating Cambridge timing or scoring standards.
