# Architecture

## Overview

MOIRA is a two-tier web app: a React SPA talking to a FastAPI JSON API backed
by PostgreSQL. No Docker/Kubernetes/microservices yet (deliberately deferred
— see project proposal).

```
┌─────────────┐      HTTPS/JSON       ┌──────────────┐      SQL       ┌────────────┐
│   React SPA │ ───────────────────▶  │   FastAPI    │ ─────────────▶ │ PostgreSQL │
│  (Vite, TS, │  ◀─────────────────── │ (SQLAlchemy, │ ◀───────────── │            │
│  Tailwind)  │        JWT auth       │   Pydantic)  │                └────────────┘
└─────────────┘                       └──────────────┘
```

## Frontend (`frontend/`)

- **React + TypeScript + Vite + Tailwind CSS.**
- `services/` — one module per API resource (`authService`, `profileService`,
  `electiveService`, `backlogService`, `facultyService`), each a thin wrapper
  around a shared `api.ts` Axios instance that attaches the JWT and base URL
  from `VITE_API_URL`.
- `context/AuthContext.tsx` — holds the current user + token (persisted to
  `localStorage`), exposes `login`, `signup`, `logout`.
- `pages/` — one route per screen (auth, dashboard, electives, backlogs,
  profile), composed from `components/`.
- Protected routes redirect to `/login` when no valid token is present.

## Backend (`backend/app/`)

- `main.py` — FastAPI app, CORS, router registration, startup table creation.
- `core/` — settings (`config.py`, env-driven), password hashing + JWT
  (`security.py`), the `get_current_user` auth dependency
  (`dependencies.py`).
- `database/` — SQLAlchemy engine/session (`connection.py`), declarative
  base (`base.py`).
- `models/` — one SQLAlchemy ORM class per table (see `docs/DATABASE.md`).
- `schemas/` — Pydantic request/response models, kept separate from ORM
  models so the API contract is explicit and stable.
- `routes/` — thin FastAPI routers; business logic lives in `services/`, not
  in route handlers.
- `services/` — `recommendation_service.py` (elective scoring, see
  `docs/RECOMMENDATION_LOGIC.md`), `backlog_service.py` (CGPA-impact ranking,
  see `docs/BACKLOG_LOGIC.md`).
- `seed/seed_data.py` — idempotent demo data loader.

## Auth flow

1. `POST /api/auth/signup` or `/api/auth/login` → backend verifies/hashes
   password with bcrypt, issues a JWT (`sub` = user id, expires per
   `ACCESS_TOKEN_EXPIRE_MINUTES`).
2. Frontend stores the token and attaches `Authorization: Bearer <token>` to
   every subsequent request via an Axios interceptor.
3. Protected routes use the `get_current_user` FastAPI dependency, which
   decodes the JWT and loads the `User` row; invalid/expired tokens return
   `401`.

## Request lifecycle example (Elective Advisor)

```
React form (interests + career goal + free text)
  → electiveService.recommend()
    → POST /api/electives/recommend  (JWT attached)
      → routes/electives.py: normalize_interests/normalize_career_goal
        → services/recommendation_service.score_elective() for each Elective row
          → sorted, top + alternatives returned with attached Faculty + FacultySchedule
      → profile.interests/career_goal/raw_intent_text persisted to Postgres
  → React renders ranked cards with match %, explanation, matched topics, faculty office hours
```

## Testing

`backend/tests/` uses an in-memory SQLite database (via a FastAPI dependency
override) so tests are fast and isolated from the real PostgreSQL instance —
see `docs/DATABASE.md` for why no migration tool is needed for this to work
cleanly.
