# Review Guidelines — first-preparation

Reviewer instructions for the Cambridge B2 First (FCE) Part 4 Trainer repository.

---

## What failure looks like here

Defect classes that critically damage this project:

1. **Cambridge Part 4 Rule Violations:**
   - Permitting answers outside the 2 to 5 words window.
   - Mutating the given keyword (changing spelling, adding suffixes like `-ing`/`-ed`).
   - Incorrect split grading logic (failing to award 1 mark when only one half of the transformation is correct).
   - Failing to normalize apostrophes (`’` vs `'`) or contractions (`didn't` vs `did not`).
2. **Security & Credential Leaks:**
   - Committing `.env`, secrets, or the SQLite database (`backend/data/fce.db*`) to git.
   - Exposing teacher/admin management endpoints without `ADMIN_PASSWORD` validation.
3. **Ergonomic & UX Regressions:**
   - Removing input padding or margins causing user text to touch prompt borders.
   - Reintroducing dark mode or unnecessary modal popups that disrupt student flow.
   - Breaking the single-page scroll layout in Timed Exam mode.
4. **Deployment Failures:**
   - Breaking Docker multi-stage build or Vite asset serving from FastAPI.

---

## Paths to skip

Do not review or comment on:
- `backend/data/fce.db*` (local database files).
- `backend/data/seeds/*.json` (curated exercise question banks, unless specifically requested).
- `frontend/dist/` (compiled static assets).
- `node_modules/` or Python virtual environments (`.venv/`, `venv/`).
- `.rsc/` internal state files.

---

## Nit cap

- **Maximum 3 nits** per review. Any minor cosmetic or stylistic comments beyond 3 are discarded to focus exclusively on correctness and architecture.

---

## Always-human paths

These paths must never be modified or merged autonomously without explicit human review:
- `docker-compose.yml` and `Dockerfile` (deployment & tunnel infrastructure).
- `backend/app/engine.py` (core Cambridge assessment logic).
- `backend/app/api/admin.py` (teacher authorization and exercise deletion/approval logic).

---

## Summary format

Every review summary must start with an exact finding count before any prose:
> `X findings: Y blockers, Z nits`
