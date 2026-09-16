"""Deterministic backlog prioritization and CGPA-impact estimation.

See docs/BACKLOG_LOGIC.md for the full formula. Grade points follow Thapar's
official 10-point grading ordinance; this is still a prototype CGPA-impact
estimate, not an official university calculation, and is labeled as such in
the API response and docs.
"""

from app.models.backlog import Backlog

GRADE_POINTS: dict[str, float] = {
    "A+": 10.0,
    "A": 10.0,
    "A-": 9.0,
    "B": 8.0,
    "B-": 7.0,
    "C": 6.0,
    "C-": 5.0,
    "E": 2.0,
    "F": 0.0,
}

# Assumed grade point earned when a backlog is eventually cleared.
# A conservative "C" (Average) pass rather than an optimistic A, since we
# cannot know the student's actual future performance.
ASSUMED_CLEAR_GRADE_POINT = 6.0


def grade_point(grade: str) -> float:
    return GRADE_POINTS.get(grade.strip().upper(), 0.0)


def estimate_cgpa_impact(
    current_cgpa: float, credits_earned: int, backlog_credits: float
) -> tuple[float, float]:
    """Return (estimated_new_cgpa, cgpa_impact) if this single backlog is cleared.

    Requires credits_earned > 0. With credits_earned == 0 there is no existing
    weighted-average baseline to blend the backlog's assumed grade into: the
    formula's new_credits term becomes just backlog_credits, which cancels out
    of new_points / new_credits algebraically — so estimated_new_cgpa collapses
    to exactly ASSUMED_CLEAR_GRADE_POINT for *every* backlog regardless of its
    credit weight, silently producing identical cgpa_impact values across
    backlogs with different credits. Callers must guard this (prioritize()
    below does) rather than call in on a zero/missing credits_earned profile.
    """
    if credits_earned <= 0:
        raise ValueError("credits_earned must be > 0 to estimate CGPA impact")
    current_points = current_cgpa * credits_earned
    new_points = current_points + (backlog_credits * ASSUMED_CLEAR_GRADE_POINT)
    new_credits = credits_earned + backlog_credits
    new_cgpa = new_points / new_credits
    return round(new_cgpa, 3), round(new_cgpa - current_cgpa, 3)


def prioritize(
    backlogs: list[Backlog], current_cgpa: float, credits_earned: int
) -> list[dict]:
    # credits_earned == 0 (unset profile, e.g. a fresh first-semester account)
    # means there is no weighted-average baseline to blend a cleared backlog
    # into — see estimate_cgpa_impact's docstring. Every backlog would report
    # the same, meaningless cgpa_impact in that state, so fall back to ranking
    # by credit weight alone and say so, instead of presenting a fake delta.
    baseline_missing = credits_earned <= 0

    scored = []
    for backlog in backlogs:
        if baseline_missing:
            new_cgpa, impact = current_cgpa, 0.0
        else:
            new_cgpa, impact = estimate_cgpa_impact(current_cgpa, credits_earned, backlog.credits)
        scored.append(
            {
                "backlog": backlog,
                "cgpa_impact": impact,
                "estimated_new_cgpa": new_cgpa,
            }
        )

    # Largest CGPA swing (in either direction) first; ties broken by higher credit weight.
    # Magnitude, not signed value, is what matters: a student already above the assumed
    # clear grade point sees a small negative dip from a low-credit backlog and a larger
    # one from a high-credit backlog — the high-credit backlog is still the more
    # consequential one to resolve. When baseline_missing, cgpa_impact is 0 for every
    # backlog so this sort falls straight through to the credits tiebreak.
    scored.sort(key=lambda item: (abs(item["cgpa_impact"]), item["backlog"].credits), reverse=True)

    results = []
    for rank, item in enumerate(scored, start=1):
        if rank == 1:
            label = "CRITICAL"
        elif rank == 2:
            label = "HIGH"
        else:
            label = "MODERATE"

        backlog = item["backlog"]
        if baseline_missing:
            explanation = (
                f"Your profile doesn't have credits earned set yet, so a CGPA-impact estimate "
                f"isn't meaningful — {backlog.course_code} is ranked by its credit weight "
                f"({backlog.credits:.0f} credits) instead. Set your CGPA and credits earned in "
                f"your profile for a personalized CGPA-impact estimate."
            )
        else:
            direction = "gain" if item["cgpa_impact"] >= 0 else "dip"
            explanation = (
                f"Clearing {backlog.course_code} ({backlog.credits:.0f} credits) is estimated to move "
                f"your CGPA by {item['cgpa_impact']:+.3f}, the "
                f"{'largest' if rank == 1 else f'#{rank} largest'} {direction} among your pending backlogs."
            )
        results.append(
            {
                "backlog": backlog,
                "priority_rank": rank,
                "priority_label": label,
                "cgpa_impact": item["cgpa_impact"],
                "estimated_new_cgpa": item["estimated_new_cgpa"],
                "explanation": explanation,
            }
        )
    return results
