# Backlog Prioritization Logic

**This is a prototype estimate, not an official university CGPA calculation.**
The grade scale below is Thapar's official 10-point grading ordinance; the
assumed 6.0 (C) grade point is grounded in TIET's auxiliary-exam grade cap
for E-grade backlogs (see §2), though the overall CGPA-impact math is still
a deliberate simplification.

## 1. Grade scale

Per Thapar's grading ordinance:

| Grade | Performance | Points |
|---|---|---|
| A+ | Outstanding | 10.0 |
| A | Excellent | 10.0 |
| A- | Very Good | 9.0 |
| B | Good | 8.0 |
| B- | Fair | 7.0 |
| C | Average | 6.0 |
| C- | Marginal | 5.0 |
| E | Exposed | 2.0 |
| F | Fail | 0.0 |

A+, A, A-, B, B-, C, and C- are pass grades. A course only becomes a
**backlog** when it's awarded **E, F, or X** (Inadequate Attendance /
Dropped / Unregistered) — that's the full set of selectable "last attempted
grade" values on the Backlog Advisor form; `I` (Incomplete) and `RA`
(Result Awaited) are temporary statuses, not backlog-causing outcomes, so
they're intentionally not offered here.

## 2. Estimated CGPA impact of clearing one backlog

A backlog's credits are **not yet counted** in the student's `credits_earned`
or `cgpa` (it was failed/not cleared). Clearing it adds new grade points and
new credits to the running total:

    current_points = current_cgpa × credits_earned
    assumed_clear_grade_point = 6.0   # see rationale below
    new_points = current_points + (backlog_credits × assumed_clear_grade_point)
    new_credits = credits_earned + backlog_credits
    estimated_new_cgpa = new_points / new_credits
    cgpa_impact = estimated_new_cgpa − current_cgpa

We assume a C (6.0 grade points) rather than an optimistic A. This isn't an
arbitrary conservative choice — it's grounded in TIET's regulations: a
backlog with an **E grade** can be cleared via the auxiliary exam, where
"candidates appearing with 'E' grade can be awarded 'C' grade as the maximum
grade." A C is therefore the regulatory ceiling for the most common backlog-
clearing route. For **F or X grades**, the student must instead re-register
and retake the full course, with no such grade cap — so 6.0 is a
conservative *floor* for those, not a precise ceiling, since the student
could realistically score higher.

The `current_grade` stored on a backlog (its prior E, F, or X outcome) does
**not** change the impact formula itself — `assumed_clear_grade_point` stays
6.0 for every backlog regardless of `current_grade`, since a backlog's
credits are not yet counted toward the degree either way. What `current_grade`
*does* change is the explanation text shown to the student: an E-grade
backlog's explanation cites the auxiliary-exam C-grade cap as the basis for
the assumption, while an F/X backlog's explanation notes the assumption is a
floor and the actual result could be higher.

**This also means a backlog can show a *negative* CGPA impact**: if a
student's current CGPA is already above 6.0, blending in an assumed
6.0-point pass pulls the weighted average down, same as one average grade
dragging down an otherwise-high GPA in real life — see §3, magnitude (not
sign) is what drives the ranking.

### 2.1 The `credits_earned = 0` edge case

If a student's profile has no `credits_earned` on record (a fresh account,
or one where only CGPA was filled in), the formula above has no existing
weighted-average baseline to blend the cleared backlog into:
`new_credits` reduces to just `backlog_credits`, which then cancels out of
`new_points / new_credits` — so `estimated_new_cgpa` collapses to exactly
`ASSUMED_CLEAR_GRADE_POINT` (6.0) for **every** backlog, regardless of its
credit weight. Two backlogs with different credits would silently show the
identical `cgpa_impact`.

`prioritize()` guards this explicitly: when `credits_earned <= 0`, it skips
the CGPA-impact formula entirely, reports `cgpa_impact: 0.0` for every
backlog, and falls back to ranking purely by credit weight (the same
tiebreak used in step 3 below), with an explanation telling the student to
fill in their CGPA and credits earned for a real estimate.

## 3. Ranking

All of a student's pending backlogs are scored independently with the
formula above (as if each were cleared in isolation), then sorted
**descending by `abs(cgpa_impact)`** — the size of the CGPA swing, regardless
of direction — with ties broken by higher credit weight.

Magnitude, not signed value, is what matters: for a student already above
the assumed clear grade point (6.0), every backlog nudges the CGPA down
slightly toward 6.0, so the *signed* impact is negative for all of them — but
a high-credit backlog still produces a bigger swing than a low-credit one,
and is still the more consequential one to resolve first. For a student
below 6.0, the signed impact is positive and larger credits simply mean
larger gains — magnitude ranking agrees with signed ranking in that case
too.

## 4. Priority labels

| Rank | Label |
|---|---|
| 1 | `CRITICAL` |
| 2 | `HIGH` |
| 3+ | `MODERATE` |

This directly mirrors "clear the backlog that will move your CGPA the most,
first" — generally the highest-credit backlog, since more credits at the
same assumed grade point produces a larger swing in the weighted average.