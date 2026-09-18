# API Reference

Base URL: `http://localhost:8000` (configurable via `VITE_API_URL` on the
frontend). All request/response bodies are JSON. Protected endpoints require
`Authorization: Bearer <token>`.

## Health

### `GET /api/health`
No auth. Returns `{"status": "ok", "service": "moira-api"}`.

## Auth

### `POST /api/auth/signup`
Body: `{ full_name, student_id, email, password }`
→ `201` `{ access_token, token_type, user }`. Creates the user and an empty
`StudentProfile`. Fails `400` on duplicate email/student ID.

### `POST /api/auth/login`
Body: `{ email, password }` → `200` `{ access_token, token_type, user }`.
`401` on wrong credentials.

### `GET /api/auth/me`
Auth required. → `200` current `UserOut`.

## Profile

### `GET /api/profile`
Auth required. → `200` `ProfileOut` for the current user.

### `PUT /api/profile`
Auth required. Body: any subset of
`{ semester, branch, cgpa, credits_earned, credits_required, career_goal, interests, raw_intent_text }`
(partial update) → `200` updated `ProfileOut`.

## Electives

### `GET /api/electives`
No auth. → `200` list of all `ElectiveOut` (with nested `faculty` + office
hours).

### `GET /api/electives/{id}`
No auth. → `200` `ElectiveOut`, or `404`.

### `POST /api/electives/recommend`
Auth required. Body:
```json
{ "free_text": "I enjoy AI and data...", "interests": ["Cybersecurity"], "career_goal": "AI/ML Engineer" }
```
→ `200`:
```json
{
  "interpreted_tags": ["Cybersecurity", "Artificial Intelligence", "Data Science"],
  "career_goal": "AI/ML Engineer",
  "top_recommendation": {
    "elective": { "...": "ElectiveOut" },
    "match_percent": 92,
    "interest_match": true,
    "career_match": true,
    "matched_topics": ["Artificial Intelligence", "Machine Learning"],
    "explanation": "..."
  },
  "alternatives": [ "...up to 5 more RecommendationOut objects" ]
}
```
Also persists the interpreted tags, career goal and raw text onto the
caller's `StudentProfile`. Scoring formula: `docs/RECOMMENDATION_LOGIC.md`.

## Faculty

### `GET /api/faculty`
No auth. → `200` list of `FacultyOut` (each with nested `schedules`).

### `GET /api/faculty/{id}`
No auth. → `200` `FacultyOut`, or `404`.

## Backlogs

### `GET /api/backlogs`
Auth required. → `200` list of the current user's `BacklogOut`.

### `POST /api/backlogs`
Auth required. Body: `{ subject, course_code, credits, course_type, current_grade }`
→ `201` created `BacklogOut`.

### `DELETE /api/backlogs/{id}`
Auth required. → `204`, or `404` if not owned by the caller.

### `POST /api/backlogs/prioritize`
Auth required, no body. Ranks all of the caller's `status="pending"`
backlogs by estimated CGPA impact. → `200`:
```json
{
  "current_cgpa": 7.2,
  "pending_count": 3,
  "prioritized": [
    {
      "backlog": { "...": "BacklogOut" },
      "priority_rank": 1,
      "priority_label": "CRITICAL",
      "cgpa_impact": 0.18,
      "estimated_new_cgpa": 7.38,
      "explanation": "..."
    }
  ]
}
```
Formula: `docs/BACKLOG_LOGIC.md`.

## Bookings

Student-facing reservation of a real, admin-entered `FacultySchedule` slot.
See `docs/BOOKING.md` for the full design (why it only ever operates on real
schedule data, never fabricated availability).

### `GET /api/bookings`
Auth required. → `200` the caller's own active (`status="booked"`) bookings,
each with the nested `schedule`.

### `POST /api/bookings`
Auth required. Body: `{ "faculty_schedule_id": <id> }` → `201` created
booking. `404` if the slot doesn't exist. `409` if it's already booked (by
any student).

### `DELETE /api/bookings/{id}`
Auth required. → `204`, or `404` if the booking doesn't exist or belongs to
someone else. Cancelling frees the slot for another student to book.

## Admin

All endpoints below require `Authorization: Bearer <token>` for a user whose
`role` is `"admin"` (checked fresh from the DB on every request via
`get_current_admin_user`, not from the token) — students get `403`,
unauthenticated callers get `401`. See `docs/ADMIN.md` for the full
authorization model, data model, and workflows.

### `GET /api/admin/dashboard`
→ `200` `{ total_electives, total_faculty, total_baskets, total_categories, total_active_bookings, recent_activity: AuditLogOut[] }`.

### Electives — `GET/POST /api/admin/electives`, `PUT/DELETE /api/admin/electives/{id}`
`GET` accepts optional `search`, `department`, `category`, `basket` query
params. `POST`/`PUT` bodies are `AdminElectiveCreate`/`AdminElectiveUpdate`
(all `Elective` fields, including `interest_tags`/`career_tags`/`faculty_id`
which the public `/api/electives` endpoints don't expose). `400` on a
duplicate `(code, department)` or an unknown `faculty_id`. `DELETE` → `204`,
or `404`.

### Faculty — `GET/POST /api/admin/faculty`, `PUT/DELETE /api/admin/faculty/{id}`
`GET` accepts optional `search`, `department`. `400` on a duplicate
`ref_code`. `DELETE` → `409` if any electives are still assigned to this
faculty member (reassign or clear `faculty_id` first); their own
`faculty_schedules` rows cascade-delete automatically.

### Schedules — `GET/POST /api/admin/schedules`, `PUT/DELETE /api/admin/schedules/{id}`
`GET` accepts optional `faculty_id`. Body includes `semester` (free text,
e.g. `"Odd 2026-27"`, empty = standing slot). `400` on an unknown
`faculty_id`.

### Bookings — `GET /api/admin/bookings`, `DELETE /api/admin/bookings/{id}`
Admin visibility over every student's slot bookings (the student-facing
`/api/bookings` endpoints only ever show the caller's own). `GET` accepts
optional `faculty_id`, returns both active and cancelled bookings
(newest first), each with the student's name/email, the faculty name, and
the nested schedule slot. `DELETE` force-cancels any booking regardless of
who made it — e.g. when a professor cancels their office hours — and is
recorded in the audit log same as any other admin mutation. See
`docs/BOOKING.md`.

### Config — `GET /api/admin/config`, `GET/PUT /api/admin/config/{key}`
Generic admin-managed key/value store. `PUT` body: `{ value, description? }`.
The well-known key `recommendation_weights` gets extra validation: `value`
must have exactly the `interest`/`career`/`syllabus`/`skill`/`academic`/
`prerequisite` keys, integers, summing to `100`, else `400`. Any other key is
stored as-is (extensible for future rules). See `docs/ADMIN.md` for how
`recommendation_weights` flows into `POST /api/recommendations`.

### `GET /api/admin/audit-log`
Optional `limit` (default 50, max 200). → `200` list of `AuditLogOut`
(`admin_id`, `action`, `entity_type`, `entity_id`, `details`, `created_at`),
most recent first. Written automatically by every admin mutation above.

## Error format

FastAPI default: `{ "detail": "message" }` with the relevant 4xx/5xx status
code.
