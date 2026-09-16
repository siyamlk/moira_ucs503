# MOIRA — Academic Advisory Platform

> "Every choice draws a path. Find your way forward."

MOIRA is a full-stack academic advisory platform built for a Software
Engineering Lab project. It turns a student's free-text interests and career
goals into ranked, explainable elective recommendations, and prioritizes
pending backlogs by estimated CGPA impact — all backed by real university
course-scheme and faculty data.

[![CI](https://github.com/siyamlk/moira/actions/workflows/ci.yml/badge.svg)](https://github.com/siyamlk/moira/actions/workflows/ci.yml)

## Table of contents

- [Problem statement](#problem-statement)
- [Features](#features)
- [Real data used](#real-data-used)
- [Architecture](#architecture)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Getting started](#getting-started)
- [API overview](#api-overview)
- [How the recommendation engine works](#how-the-recommendation-engine-works)
- [How backlog prioritization works](#how-backlog-prioritization-works)
- [Known limitations](#known-limitations)

## Problem statement

Students don't think in four-digit course codes. Picking electives and
knowing which backlog to clear first usually means digging through PDFs and
asking around. MOIRA takes a student's plain-language interests and career
goals, maps them to real elective offerings and faculty expertise, and gives
a transparent, ranked recommendation — plus a deterministic, explainable
priority order for pending backlogs based on their CGPA impact.

## Features

- **JWT authentication** — signup/login with bcrypt-hashed passwords.
- **Student profile** — semester, CGPA, credits, career goal, interests;
  persists across sessions.
- **Elective Advisor** — free text + interest/career chips → normalized tags
  → rule-based scoring against real course data → ranked recommendations
  with a plain-language explanation and matched faculty by specialization.
- **Backlog Advisor** — add pending backlogs, get a deterministic priority
  ranking (CRITICAL/HIGH/MODERATE) with estimated CGPA impact per course.
- **Faculty directory** — searchable, real faculty data (name, title,
  specialization, email, office room where available).

## Real data used

- **Electives**: transcribed from the official 2025 B.E. CSE and COE course
  scheme documents (Professional Elective baskets I–IV) — 96 real courses
  with real codes and credits.
- **Faculty**: 211 CSE faculty + 65 ECE faculty from official department
  directories (name, designation, specialization, email; office room where
  the source data had it).
- Mechanical, Civil, and ENC branch data has not been added yet — the
  pipeline (`backend/app/seed/data/`, `backend/app/seed/seed_data.py`)
  is ready to take more CSV/scheme sources the same way.
- Where source data doesn't exist (e.g. CSE faculty office hours, per-course
  syllabi), MOIRA leaves it empty and says so in the UI ("Office hours not
  yet available") rather than inventing it.

## Architecture

MOIRA is a two-tier web app: a React SPA talking to a FastAPI JSON API
backed by PostgreSQL. No Docker/Kubernetes/microservices — deliberately
deferred to keep a Lab-scale project simple to run and reason about.

```
                    HTTPS / JSON (JWT bearer)
 ┌────────────────────┐  ─────────────────────▶   ┌──────────────────────┐        SQL        ┌─────────────┐
 │      React SPA      │                           │        FastAPI       │ ────────────────▶ │  PostgreSQL │
 │  Vite · TS · Router  │  ◀─────────────────────   │  SQLAlchemy · Pydantic│ ◀──────────────── │             │
 │  Tailwind · Axios    │                           │                       │                   └─────────────┘
 └────────────────────┘                            └──────────────────────┘
          │                                                    │
          │ services/*.ts — one module per resource            │ routes/ (thin) → services/ (logic) → models/ (ORM)
          │ AuthContext — JWT + user in localStorage            │ recommendation/ — scoring engine, career matching
          ▼                                                    ▼
   pages/ per screen, composed                         seed/seed_data.py loads real
   from components/                                    CSV faculty + elective data
```

**Frontend** (`frontend/`)
- `services/` — one module per API resource (`authService`, `profileService`,
  `electiveService`, `backlogService`, `facultyService`), each a thin wrapper
  around a shared `api.ts` Axios instance that attaches the JWT and base URL
  from `VITE_API_URL`.
- `context/AuthContext.tsx` — holds the current user + token (persisted to
  `localStorage`), exposes `login`, `signup`, `logout`.
- `pages/` — one route per screen (auth, dashboard, electives, backlogs,
  profile), composed from `components/`. Protected routes redirect to
  `/login` when no valid token is present.

**Backend** (`backend/app/`)
- `main.py` — FastAPI app, CORS, router registration, startup table creation.
- `core/` — settings (`config.py`, env-driven), password hashing + JWT
  (`security.py`), the `get_current_user` auth dependency (`dependencies.py`).
- `database/` — SQLAlchemy engine/session (`connection.py`), declarative base
  (`base.py`).
- `models/` — one SQLAlchemy ORM class per table.
- `schemas/` — Pydantic request/response models, kept separate from ORM
  models so the API contract is explicit and stable.
- `routes/` — thin FastAPI routers; business logic lives in `services/` and
  `recommendation/`, not in route handlers.
- `recommendation/` — the rule-based scoring engine, profile analysis,
  career matching, and explanation generation for the Elective Advisor.
- `services/` — `recommendation_service.py` (orchestrates elective scoring),
  `backlog_service.py` (CGPA-impact ranking).
- `seed/seed_data.py` — idempotent loader for real course/faculty CSVs plus
  one demo account.

**Auth flow**: signup/login issues a JWT (`sub` = user id) signed with
`JWT_SECRET`; the frontend attaches it as `Authorization: Bearer <token>` via
an Axios interceptor; protected FastAPI routes decode it through the
`get_current_user` dependency and return `401` on anything invalid/expired.

**Request lifecycle example** (Elective Advisor): a React form submits
interests + career goal + free text → `electiveService.recommend()` →
`POST /api/electives/recommend` (JWT attached) → the route normalizes free
text into interest/career tags → `recommendation_service` scores every
`Elective` row against those tags → sorted results (top pick + alternatives)
are returned with matched faculty and office hours attached, and the
interpreted tags are persisted back onto the caller's profile.

Full deep-dive, including testing strategy: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
Schema reference: [docs/DATABASE.md](docs/DATABASE.md).

## Tech stack

| Layer | Choices |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, React Router, Axios |
| Backend | Python, FastAPI, SQLAlchemy 2, Pydantic 2, python-jose (JWT), passlib + bcrypt |
| Database | PostgreSQL |
| Testing | pytest (backend, in-memory SQLite), `tsc -b` build check (frontend) |
| CI | GitHub Actions — install, build, test on every push/PR |

Docker is intentionally not used yet — see the project proposal.

## Project structure

```
moira/
├── frontend/              React + TypeScript + Vite + Tailwind
│   └── src/
│       ├── components/    UI building blocks, grouped by feature
│       ├── pages/         One folder per route
│       ├── services/      Axios API clients, one per backend resource
│       ├── context/       AuthContext (JWT + user session)
│       └── utils/         Tag/branch/format helpers shared across pages
├── backend/                FastAPI + SQLAlchemy + Pydantic
│   └── app/
│       ├── core/           Settings, security (JWT/bcrypt), auth dependency
│       ├── database/       SQLAlchemy engine/session/base
│       ├── models/         ORM models (one per table)
│       ├── schemas/        Pydantic request/response contracts
│       ├── routes/         Thin FastAPI routers
│       ├── recommendation/ Scoring engine, career matching, explanations
│       ├── services/       Recommendation + backlog orchestration
│       └── seed/           Real CSV data + idempotent seed script
├── docs/                    Architecture, API, database, recommendation & backlog logic
└── .github/workflows/       CI (frontend build + backend tests)
```

## Getting started

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+ (running locally, or a connection string to an existing instance)

### 1. Database

Create a database and user (adjust to taste):

```sql
CREATE USER moira_user WITH PASSWORD 'moira_password';
CREATE DATABASE moira OWNER moira_user;
```

> If you don't have PostgreSQL installed and don't want a system-wide
> install, EnterpriseDB also ships a portable zip of the Postgres binaries
> (no installer, no admin rights) — `initdb` a data directory anywhere and
> `pg_ctl start` it. That's what this workspace's dev instance uses.

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash; use .venv\Scripts\activate on cmd/PowerShell
pip install -r requirements.txt

cp .env.example .env            # edit DATABASE_URL / JWT_SECRET if needed

python -m app.seed.seed_data    # creates tables + seeds faculty/electives/demo user
uvicorn app.main:app --reload --port 8000
```

Backend runs at `http://localhost:8000`. Interactive API docs at
`http://localhost:8000/docs`.

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env            # VITE_API_URL=http://localhost:8000/api
npm run dev
```

Frontend runs at `http://localhost:5173`.

### 4. Log in

- **Demo account**: `alex.chen@thapar.edu` / `Demo@1234` (seeded with a
  profile, interests, and 3 sample backlogs so you can try every feature
  immediately).
- Or sign up a new account from the app.

### 5. Run tests

```bash
cd backend
source .venv/Scripts/activate
pytest -v
```

19 tests covering auth, profile, elective recommendation scoring/ranking,
and backlog prioritization/CGPA-impact math.

## API overview

Full reference: [docs/API.md](docs/API.md).

```
GET  /api/health
POST /api/auth/signup            POST /api/auth/login       GET /api/auth/me
GET  /api/profile                PUT  /api/profile
GET  /api/electives               GET /api/electives/{id}    POST /api/electives/recommend
GET  /api/backlogs                POST /api/backlogs         POST /api/backlogs/prioritize
GET  /api/faculty                 GET /api/faculty/{id}
```

## How the recommendation engine works

Free text is mapped to a fixed vocabulary of interest/career tags via
keyword matching (no ML, fully deterministic and explainable), then each
elective is scored 0–100 against those tags: 45% interest overlap, 30%
career-goal alignment, 20% topic overlap, plus a small relevance bonus.
Full formula: [docs/RECOMMENDATION_LOGIC.md](docs/RECOMMENDATION_LOGIC.md).

## How backlog prioritization works

Each pending backlog's estimated CGPA impact is computed from the student's
current CGPA and credit load, assuming a conservative pass grade if cleared;
backlogs are ranked by the *magnitude* of that swing, so higher-credit
backlogs are surfaced first regardless of whether the student is above or
below the assumed grade point. Full formula, and why it's a *prototype*
estimate rather than an official calculation:
[docs/BACKLOG_LOGIC.md](docs/BACKLOG_LOGIC.md).

## Known limitations

- Only CSE + COE elective data and CSE + ECE faculty data are loaded;
  Mechanical, Civil, and ENC are not yet included.
- No office-hours schedule data exists for CSE faculty (only ECE has room
  numbers); the UI says so rather than fabricating times.
- No syllabus-level detail (prerequisites, descriptions) per elective —
  only what the scheme documents' summary tables contain (code, title,
  credits).
- "Suggested faculty" on a recommendation is a live keyword match between
  the elective's topics and each faculty member's specialization — the
  source scheme documents don't assign a fixed instructor per elective
  section, so this is deliberately not a fabricated FK.
- Backlog CGPA-impact is a documented prototype formula (see
  docs/BACKLOG_LOGIC.md), not an official university calculation.
- Enroll/syllabus buttons on elective recommendations are intentionally
  disabled — no enrollment system exists yet.
- Docker/CI-for-deploy is out of scope for now (see project proposal).

## License

Educational project.
