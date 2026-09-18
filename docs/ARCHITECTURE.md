# Architecture

## Overview

MOIRA is a two-tier web app: a React SPA talking to a FastAPI JSON API backed
by PostgreSQL. Each tier is containerized (`backend/Dockerfile`,
`frontend/Dockerfile`, wired together with Postgres in `docker-compose.yml`
at the repo root) and CI publishes both images to GHCR on every merge to
main — see *Docker & CI/CD* below. No Kubernetes/microservices split yet;
that stays deliberately deferred until actual load justifies it (see the
"Architectural Scaling" section of the README).

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
   `ACCESS_TOKEN_EXPIRE_MINUTES`). The token never carries a role claim.
2. Frontend stores the token and attaches `Authorization: Bearer <token>` to
   every subsequent request via an Axios interceptor.
3. Protected routes use the `get_current_user` FastAPI dependency, which
   decodes the JWT and loads the `User` row; invalid/expired tokens return
   `401`. Admin-only routes additionally depend on `get_current_admin_user`,
   which checks `User.role == "admin"` freshly off that same row on every
   request — see `docs/ADMIN.md`.

## Admin subsystem

A second actor (`role = "admin"` on `User`, default `"student"`) with its own
route package (`routes/admin/`), its own schemas (`schemas/admin.py`), and a
full CRUD surface over the academic data the advisory engines consume
(`Elective`, `Faculty`, `FacultySchedule`) plus a generic `AcademicConfig`
key/value store and an `AuditLog` of every admin mutation. The frontend
mirrors this with a parallel `/admin/*` route tree (`AdminRoute` +
`AdminLayout`, alongside the existing `ProtectedRoute` + `AppLayout`) so
student and admin surfaces stay structurally independent while sharing the
same design system, auth context, and Axios client. Full details, including
the authorization model, data model, and the "admin manages data → engine
consumes it" flow for `recommendation_weights`: `docs/ADMIN.md`.

## Request lifecycle example (Elective Advisor)

```
React form (interests, career goals, skills, free text)
  → recommendationService.recommend()
    → POST /api/recommendations  (JWT attached)
      → routes/recommendations.py
        → recommendation/profile_analyzer.analyze_profile() — tags + custom interest terms
        → recommendation/recommendation_service.generate_recommendations()
            → app/services/academic_config_service.get_recommendation_weights() (admin-tunable)
            → recommendation/scoring_engine.score_elective() for each eligible Elective row
            → recommendation/basket_service.build_basket_recommendations() — group by EFB basket
            → recommendation/explanation_service.build_recommendation_texts()
          → basket-level + individual-course results, sorted, with score breakdowns
      → profile fields persisted to Postgres
  → React renders ranked basket + course cards with score breakdown, matched evidence,
    prerequisite checklist, and attached Faculty + FacultySchedule
```

## Docker & CI/CD

- `backend/Dockerfile` — plain `python:3.11-slim` + `pip install -r
  requirements.txt`; `psycopg2-binary` means no separate `libpq`/build-tool
  layer is needed.
- `frontend/Dockerfile` — multi-stage: `node:20-alpine` runs `npm run
  build`, then the static `dist/` output is copied into an `nginx:alpine`
  stage (`nginx.conf` adds the SPA fallback React Router needs). `VITE_API_URL`
  is a build arg — Vite env vars are compiled into the bundle, not read at
  container runtime, so it must be supplied at `docker build`/`docker compose
  build` time, not via a runtime environment variable.
- `docker-compose.yml` (repo root) wires Postgres + backend + frontend
  together for local development or a staging box — `docker compose up
  --build`, then `docker compose exec backend python -m app.seed.seed_data`
  once.
- CI (`.github/workflows/ci.yml`) adds a `docker` job after the existing
  frontend-build and backend-test jobs: it builds both images on every push
  and pull request, and additionally pushes them to GitHub Container
  Registry (`ghcr.io/<repo>-backend`, `ghcr.io/<repo>-frontend`) on pushes to
  `main`. This is the project's zero-budget stand-in for a "staging
  deployment" step — images land in a registry ready to run, without paying
  for a hosted environment.

## Caching (Redis)

`app/services/cache_service.py` is a small, optional caching layer over two
specific, read-heavy, rarely-changing public endpoints — not a general
"we use Redis" story:

- `GET /api/electives` (unfiltered listing only — a department-filtered
  request always reads the DB directly, since department values aren't
  enumerable up front for invalidation)
- `GET /api/faculty` (including each schedule's live `is_booked` flag — see
  `docs/BOOKING.md`)

Both are hit on nearly every page load (the browse/recommendation flows) and
only change when something mutates the underlying data — an admin CRUD
action, or, for faculty, a student booking/cancelling a slot. Every one of
those mutation routes calls `invalidate(...)` on the relevant cache key
right after its `db.commit()`, so the cache never serves data staler than
the last actual write (bounded further by a 5-minute TTL as a backstop).

Redis is treated as a pure performance layer, never a dependency the app can
fail on: `get_cached`/`set_cached`/`invalidate` each wrap their Redis call in
a `try/except` and silently fall back to hitting PostgreSQL directly. This
means the app, and the full test suite, run identically whether or not a
Redis instance is present — no Redis is started in CI or in
`backend/tests/`, and nothing there needs to change to keep passing.
`docker-compose.yml` runs a `redis:7-alpine` service for local development;
`REDIS_URL` (default `redis://localhost:6379/0`, overridden to
`redis://redis:6379/0` inside Compose) is the only new setting.

## Testing

`backend/tests/` uses an in-memory SQLite database (via a FastAPI dependency
override) so tests are fast and isolated from the real PostgreSQL instance —
see `docs/DATABASE.md` for why no migration tool is needed for this to work
cleanly.
