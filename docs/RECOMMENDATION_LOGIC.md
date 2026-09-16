# Elective Recommendation Logic

MOIRA's Elective Advisor is a **transparent, rule-based** recommendation
engine. There is no machine learning model and no external API call — every
score can be traced back to a simple, auditable formula. This document is the
source of truth for that formula; `backend/app/services/recommendation_service.py`
implements it.

## 1. Free text → structured tags

A student's free-text intent (e.g. *"I enjoy AI, data analysis, and
programming, and I want to work in healthcare predictive systems"*) is
normalized into a fixed vocabulary of canonical **interest tags** and
**career tags** using keyword matching.

- `INTEREST_KEYWORDS` and `CAREER_KEYWORDS` in `recommendation_service.py`
  map each canonical tag (e.g. `"Machine Learning"`) to a list of
  synonyms/phrases (`"ml"`, `"machine learning"`).
- Matching is case-insensitive substring/word-boundary matching — no ML
  inference, so results are 100% reproducible for the same input text.
- Tags selected explicitly via UI chips are merged with tags inferred from
  free text (`normalize_interests`), de-duplicated, order preserved.

## 2. Scoring an elective (0–100)

For each elective, MOIRA compares the student's `interest_tags` and
`career_tags` against the elective's own `interest_tags`, `career_tags` and
`topics` metadata:

| Component | Weight | Formula |
|---|---|---|
| Interest match | 45 pts | `45 × (matched interest tags / total student interest tags)` |
| Career alignment | 30 pts | `30` if any student career tag matches the elective's career tags, else `0` |
| Topic overlap | 20 pts | `20 × (matched topics / total elective topics)` |
| Relevance bonus | 5 pts | `5` if there is any match at all (interest, career, or topic) |

The four components are summed and capped at 100, then rounded to the
nearest integer. An elective with **zero overlap** scores exactly `0` — it is
never artificially inflated.

## 3. Ranking & explanation

- All electives are scored and sorted descending by `match_percent`.
- The highest-scoring elective is returned as `top_recommendation`; the next
  five as `alternatives`.
- Each recommendation includes a generated, human-readable `explanation`
  string built from which components actually matched (see
  `build_explanation`), e.g.:
  > "Machine Learning & Predictive Analytics aligns strongly with your
  > interests in Artificial Intelligence, Machine Learning and your stated
  > goal of AI/ML Engineer."
- The matched faculty and their office-hours schedule are attached via the
  `Elective.faculty` relationship so the UI can show "who to talk to" next
  to each recommendation.

## 4. Suggested faculty (`suggest_faculty`)

The source course-scheme documents list elective baskets without a fixed
instructor per section (assignment varies by offering semester), so
`Elective.faculty_id` is always `null` for seeded data. Instead, each
recommendation includes a live `suggested_faculty` list: faculty whose
`specialization` + `research_interests` text contains a case-insensitive
match for one of the student's interest tags, restricted to the elective's
own department, ranked by number of matching tags (top 3). This is a
transparent keyword match computed at request time — not a stored,
potentially stale or fabricated instructor assignment.

## 5. Why rule-based, not ML?

The project proposal calls for a transparent, explainable advisor students
can trust and faculty can audit — every score must be traceable to a
specific rule. A learned ranking model would need a large labeled dataset of
past student outcomes that does not exist yet. This design can be swapped
for a learned ranker later without changing the API contract.
