# Database Schema

PostgreSQL via SQLAlchemy ORM. Tables are created automatically on backend
startup via `Base.metadata.create_all()` — no migration tool (Alembic) is
used yet to keep the project simple; add Alembic if the schema needs to
evolve against a populated production database later.

## Entities

### `users`
| Column | Type | Notes |
|---|---|---|
| id | PK | |
| full_name | string | |
| student_id | string | unique |
| email | string | unique |
| hashed_password | string | bcrypt hash, never plaintext |
| created_at | datetime | |

### `student_profiles` (1:1 with `users`)
| Column | Type | Notes |
|---|---|---|
| id | PK | |
| user_id | FK → users.id | unique |
| semester | int | |
| branch | string | |
| cgpa | float | 0–10 scale |
| credits_earned | int | |
| credits_required | int | degree total, default 160 |
| career_goal | string | free text, also tag-normalized |
| interests | JSON list[str] | canonical interest tags |
| raw_intent_text | string | last free-text intent submitted |

### `faculty`
| Column | Type | Notes |
|---|---|---|
| id | PK | |
| ref_code | string | unique short code (e.g. `ECE-KBS`, `CSE-042`) |
| name, title, department | string | |
| specialization | string | |
| research_interests | JSON list[str] | `specialization` split on commas |
| office_location | string | room number where the source data has it (e.g. ECE); empty otherwise |
| email, photo_url, profile_url | string | from the source faculty directory; empty if unavailable |

### `faculty_schedules` (N:1 with `faculty`)
| Column | Type | Notes |
|---|---|---|
| id | PK | |
| faculty_id | FK → faculty.id | |
| day | string | e.g. `Monday` |
| start_time, end_time | string | `HH:MM` |
| room | string | |
| note | string | e.g. `Office Hours` |

### `electives`
| Column | Type | Notes |
|---|---|---|
| id | PK | |
| code | string | e.g. `UCS531` — **unique per (code, department)**, not globally unique, since the same course code is legitimately offered under multiple branches |
| title, department, description | string | `description` empty (not in source scheme summary tables) |
| credits | float | |
| prerequisites | string | empty (not in source scheme summary tables) |
| category | string | e.g. `Professional Elective` |
| topics | JSON list[str] | auto-derived from `title` via the recommendation engine's keyword vocabulary |
| interest_tags | JSON list[str] | same derivation as `topics`, used by recommendation engine |
| career_tags | JSON list[str] | auto-derived from `title`; often empty since course titles rarely contain career-goal phrasing |
| faculty_id | FK → faculty.id | always null for seeded data — the source scheme documents don't assign a fixed instructor per elective section (see `suggest_faculty` in `docs/RECOMMENDATION_LOGIC.md`) |

### `backlogs` (N:1 with `users`)
| Column | Type | Notes |
|---|---|---|
| id | PK | |
| user_id | FK → users.id | |
| subject, course_code | string | |
| credits | float | |
| course_type | string | e.g. `Core Course` |
| current_grade | string | last attempted grade, informational |
| status | string | `pending` \| `cleared` |
| created_at | datetime | |

## Relationships

```
User 1───1 StudentProfile
User 1───N Backlog
Faculty 1───N FacultySchedule
Faculty 1───N Elective
```

## Seed data

`backend/app/seed/seed_data.py` loads real data from
`backend/app/seed/data/`:

- `faculty_cse.csv` (211 rows) and `faculty_ece.csv` (65 rows) — real
  Thapar CSED/ECED faculty directories.
- `electives_cse.csv` and `electives_coe.csv` (48 rows each) — real
  Professional Elective baskets transcribed from the official 2025 B.E.
  CSE/COE course scheme documents.

It also seeds one **demo student account**
(`alex.chen@thapar.edu` / `Demo@1234`) with a sample profile and 3 pending
backlogs, clearly a demo account (not sourced from any real record), so the
app can be tried immediately without signing up. Mechanical, Civil, and ENC
branch data is not yet included — add a CSV + a `FACULTY_SOURCES`/
`ELECTIVE_SOURCES` entry the same way to extend coverage.
