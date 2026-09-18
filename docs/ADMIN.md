# Admin Subsystem

A second actor on top of the existing student-facing platform: an **Admin**
who maintains the academic data (electives, faculty, schedules) and a small
set of academic configuration values the advisory engines read. This
document covers the authorization model, data model, endpoints, and the
"admin manages data → engine consumes it" flow. Full endpoint reference:
`docs/API.md`. Schema: `docs/DATABASE.md`.

## Why

Before this feature, `Elective`/`Faculty`/`FacultySchedule` data was
**read-only through the API** — the only way any of it entered the system
was a one-off CSV seed script run manually from a terminal
(`python -m app.seed.seed_data`). There was no way to fix a course
description, add an elective when the curriculum changes, correct a faculty
member's office hours, or retune the recommendation engine's scoring weights
without editing CSVs and re-seeding by hand.

## Authorization model

- `User.role` (`"student"` default, or `"admin"`) is the only new field on
  the existing auth model. **Nobody can self-elevate** — there is no
  signup/API path that sets `role="admin"`; it's set by the seed script or a
  direct DB update only.
- The JWT itself is **unchanged** — still just `{"sub": user_id, "exp": ...}`.
  `get_current_user` already re-fetches the `User` row from the DB on every
  request (never trusts the token beyond the id); the new
  `get_current_admin_user` dependency (`app/core/dependencies.py`) just adds
  `if current_user.role != "admin": raise HTTPException(403)` on top of that
  same fresh row. A demoted admin loses access on their very next call, not
  at token expiry.
- Every `/api/admin/*` route depends on `get_current_admin_user`:
  unauthenticated → `401`, authenticated student → `403`.
- On the frontend, `AdminRoute` (parallel to the existing `ProtectedRoute`)
  redirects unauthenticated users to `/login` and non-admins to `/dashboard`.
  This is a UX convenience only — as with every route in this app, the real
  enforcement is server-side; a stale client-side `role` (e.g. an admin
  demoted mid-session, not refreshed until next page load) can never bypass
  `get_current_admin_user`.

## Default admin account

The seed script (`backend/app/seed/seed_data.py::seed_admin`) creates one
fixed dev account:

```
email:    admin@moira.app
password: AdminPass123!
```

**This is a dev-only convenience. Rotate the password or delete/replace this
account before any real deployment.** To promote a different existing user
to admin instead, update the DB directly:

```sql
UPDATE users SET role = 'admin' WHERE email = 'someone@example.com';
```

## Data model

No new "Course" entity was introduced. The database has exactly one course
catalog table, `Elective` — `Backlog` rows are free-text and were never
linked to a catalog. The requirements' separate "Courses" and "Electives"
admin sections would have meant either duplicating that table (violating
"avoid duplicated data") or maintaining two admin UIs over identical data —
so both map onto **one** backend resource (`/api/admin/electives`) and one
frontend page ("Courses & Electives"), filterable by department/category/
basket/search.

New tables (see `docs/DATABASE.md` for full column lists):
- **`audit_log`** — one row per admin mutation (`admin_id`, `action`,
  `entity_type`, `entity_id`, `details`, `created_at`). Written by a single
  explicit `record_audit(...)` call at the end of each mutating admin route
  (`app/services/audit_service.py`) — no decorator/middleware magic, since
  ~20 call sites don't justify the abstraction.
- **`academic_config`** — generic `key`/`value` (JSON) store for admin-tuned
  rules, seeded with `recommendation_weights` and `elective_categories`.

Existing tables gained one column each: `users.role`,
`faculty_schedules.semester` (see `docs/DATABASE.md` for how this is
backfilled onto an already-populated Postgres DB without a migration tool).

## Endpoints

Full reference: `docs/API.md#admin`. Summary:

| Resource | Endpoints |
|---|---|
| Dashboard | `GET /api/admin/dashboard` |
| Electives | `GET/POST /api/admin/electives`, `PUT/DELETE /api/admin/electives/{id}` |
| Faculty | `GET/POST /api/admin/faculty`, `PUT/DELETE /api/admin/faculty/{id}` |
| Schedules | `GET/POST /api/admin/schedules`, `PUT/DELETE /api/admin/schedules/{id}` |
| Bookings | `GET /api/admin/bookings`, `DELETE /api/admin/bookings/{id}` |
| Config | `GET /api/admin/config`, `GET/PUT /api/admin/config/{key}` |
| Audit log | `GET /api/admin/audit-log` |

Notable data-integrity behavior: deleting a `Faculty` with electives still
assigned to them returns `409 Conflict` (reassign or clear `faculty_id`
first) rather than silently orphaning those courses; their `FacultySchedule`
rows cascade-delete automatically (existing `cascade="all, delete-orphan"`
relationship, unchanged).

## Recommendation weights: admin manages data, the engine still scores

The requirement that "the recommendation engine should continue to be
responsible for scoring/ranking" — admin only manages the data/config it
runs on — is concretely implemented like this:

```
Admin edits weights (must sum to 100)
  → PUT /api/admin/config/recommendation_weights
    → validated + upserted into academic_config
      → app/services/academic_config_service.get_recommendation_weights(db)
        → app/recommendation/recommendation_service.generate_recommendations()
          → app/recommendation/scoring_engine.score_elective(weights=...)
            → POST /api/recommendations response includes the weights used
```

`scoring_engine.score_elective()` still owns all scoring logic — the
`weights` parameter defaults to the hardcoded `SCORE_WEIGHTS` constant when
not supplied, so every existing caller/test that doesn't pass `weights`
behaves identically. Admin input only ever supplies numbers into that
existing, unchanged formula; it never touches ranking logic itself. A
submitted weights object that doesn't have exactly the six known component
keys, as integers, summing to 100, is rejected with `400` before it's ever
saved.

## Frontend

- `/admin`, `/admin/electives`, `/admin/faculty`, `/admin/schedules`,
  `/admin/bookings`, `/admin/config` — nested under `AdminRoute` + `AdminLayout`
  (`frontend/src/layouts/AdminLayout.tsx`), structurally parallel to the
  student area's `ProtectedRoute` + `AppLayout`, sharing the same auth
  context, Axios client (`services/api.ts`), and Tailwind design tokens —
  no separate design system.
- Two small shared components (`components/admin/AdminTable.tsx`,
  `ConfirmDialog.tsx`) back all four CRUD pages' list/delete-confirm UI,
  since five near-identical hand-rolled tables would themselves be the
  duplicated logic the project guidelines warn against. Create/edit forms
  stay per-page (built from the existing `TextField`/`TagListInput`), since
  each resource's fields differ enough that a generic form abstraction
  wasn't worth it.
- The elective form's category dropdown is populated from
  `GET /api/admin/config/elective_categories` rather than hardcoded, with a
  small client-side fallback list if that config key hasn't been seeded yet.
- Admin users see a small "Admin" link in the normal student `Navbar`
  (`user.role === "admin"` only) to discover the area; students see no
  change to their navbar at all.

## Testing

`backend/tests/test_admin.py` covers: unauthenticated (`401`) / student
(`403`) / admin access to every admin route; full elective/faculty/schedule
CRUD including validation failures and the faculty-delete-with-assigned-
electives `409`; `recommendation_weights` update reflected in a subsequent
`POST /api/recommendations` call and rejected when it doesn't sum to `100`;
audit log entries recorded with the correct actor/action/entity; and a
regression check that fresh signups still default to `role="student"`. All
pre-existing tests were left unmodified and continue to pass.
