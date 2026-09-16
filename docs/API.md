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

## Error format

FastAPI default: `{ "detail": "message" }` with the relevant 4xx/5xx status
code.
