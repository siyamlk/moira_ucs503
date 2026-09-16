"""Aggregates individual elective scores into EFB basket-level
recommendations. The EFB source document groups every Elective I-IV
sequence under a named basket (e.g. "Data Science") — a student commits
to one basket and takes all four electives from it, so the primary
recommendation unit should be the basket, not an arbitrary single course.

This module only aggregates data already computed by scoring_engine /
recommendation_service — it does not score anything itself.
"""

from collections import defaultdict
from dataclasses import dataclass

from app.schemas.recommendation import RecommendationItem

_SLOT_ORDER = {"Elective I": 0, "Elective II": 1, "Elective III": 2, "Elective IV": 3}


@dataclass
class BasketRecommendation:
    basket_name: str
    match_percentage: int
    electives: list[RecommendationItem]
    matched_interests: list[str]
    matched_career_goals: list[str]
    why_this_basket_matches: str


def _basket_explanation(basket_name: str, electives: list[RecommendationItem]) -> str:
    matched_interests = sorted({t for e in electives for t in e.matched_interests})
    matched_career = sorted({t for e in electives for t in e.matched_career_goals})
    course_list = ", ".join(f"{e.course_code} ({e.elective.category})" for e in electives)

    parts = []
    if matched_interests:
        parts.append(f"your stated interest(s) in {', '.join(matched_interests)}")
    if matched_career:
        parts.append(f"your career goal's focus on {', '.join(matched_career)}")

    if not parts:
        return f"The {basket_name} basket ({course_list}) didn't match your stated interests or career goal directly."
    avg = round(sum(e.match_percentage for e in electives) / len(electives)) if electives else 0
    return (
        f"The {basket_name} basket matches {' and '.join(parts)}, averaging {avg}% across its "
        f"courses: {course_list}."
    )


def build_basket_recommendations(items: list[RecommendationItem]) -> list[BasketRecommendation]:
    """Groups already-scored RecommendationItems by their Elective.basket
    and computes each basket's aggregate match_percentage as the average
    of its member courses' individual scores. Items with no basket (open
    electives, and the handful of CSE/COE courses not grouped under a
    named EFB basket in the source document) are excluded — basket-level
    recommendation only applies where a real basket membership exists."""
    grouped: dict[str, list[RecommendationItem]] = defaultdict(list)
    for item in items:
        if item.elective.basket:
            grouped[item.elective.basket].append(item)

    baskets: list[BasketRecommendation] = []
    for basket_name, electives in grouped.items():
        electives = sorted(electives, key=lambda e: _SLOT_ORDER.get(e.elective.category, 99))
        avg_score = round(sum(e.match_percentage for e in electives) / len(electives))
        matched_interests = sorted({t for e in electives for t in e.matched_interests})
        matched_career = sorted({t for e in electives for t in e.matched_career_goals})
        baskets.append(
            BasketRecommendation(
                basket_name=basket_name,
                match_percentage=avg_score,
                electives=electives,
                matched_interests=matched_interests,
                matched_career_goals=matched_career,
                why_this_basket_matches=_basket_explanation(basket_name, electives),
            )
        )

    baskets.sort(key=lambda b: b.match_percentage, reverse=True)
    return baskets
