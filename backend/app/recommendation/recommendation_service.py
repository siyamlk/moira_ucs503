"""Orchestrates the elective recommendation system: pulls eligible
electives from the database, scores each one with scoring_engine, builds
its explanation with explanation_service, and assembles the primary
recommendation / alternatives / full eligible list the API returns.

This is the only place that talks to the database — scoring_engine,
syllabus_matcher, career_matcher and explanation_service are all pure
functions over plain data, so they're independently testable.
"""

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.core.constants import OPEN_ELECTIVE_DEPARTMENT
from app.models.elective import Elective
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.recommendation.basket_service import BasketRecommendation, build_basket_recommendations
from app.recommendation.explanation_service import build_recommendation_texts
from app.recommendation.profile_analyzer import analyze_profile, normalize_elective_slot
from app.recommendation.scoring_engine import SCORE_WEIGHTS, score_elective
from app.schemas.elective import ElectiveOut
from app.schemas.recommendation import (
    AllEligibleItem,
    BasketRecommendationOut,
    PrerequisiteCheckOut,
    RecommendationItem,
    RecommendationRequest,
    RecommendationResponse,
    ScoreBreakdownOut,
    ScoreComponentOut,
)


def _dedupe_by_code(electives: list[Elective]) -> list[Elective]:
    """The same course code can legitimately exist as more than one DB row
    — one per department/branch it's offered under (e.g. UCS542 "UI & UX
    Specialist" exists once for "Computer Science and Engineering" and
    again for "Computer Engineering"; see Elective.code's docstring). The
    department filter above normally narrows this to one row, but that
    filter is skipped entirely whenever a student's profile has no branch
    set yet (StudentProfile.branch defaults to "" for every new signup) —
    so without this dedup, a student who hasn't picked their branch sees
    every shared course listed twice (once per department row), and
    basket-level averages get computed over duplicated, not independent,
    courses. Keeps the first row encountered per code — they're otherwise
    identical for scoring purposes since only the department differs."""
    seen: set[str] = set()
    deduped: list[Elective] = []
    for elective in electives:
        if elective.code in seen:
            continue
        seen.add(elective.code)
        deduped.append(elective)
    return deduped


def _basket_out(basket: BasketRecommendation) -> BasketRecommendationOut:
    return BasketRecommendationOut(
        basket_name=basket.basket_name,
        match_percentage=basket.match_percentage,
        electives=basket.electives,
        matched_interests=basket.matched_interests,
        matched_career_goals=basket.matched_career_goals,
        why_this_basket_matches=basket.why_this_basket_matches,
    )


def _persist_profile_updates(
    profile: StudentProfile, request: RecommendationRequest, db: Session, student_profile_provided: bool
) -> None:
    """Save whatever new info this call supplied back onto the stored
    profile, so the next call (or the elective advisor UI) doesn't need it
    re-entered.

    When student_profile_provided is True (MOIRA's own UI always sends a
    full student_profile — see RecommendationsPage.tsx), every list/chip
    field is saved exactly as submitted, including empty ones. Previously
    this used a truthy check (`if rp.interests:`) to decide what to
    overwrite, which meant an explicitly-cleared chip (submitted as `[]`)
    was silently skipped and the old stored value kept living in the DB
    forever — the student could never actually remove a stale interest,
    career goal, skill, etc. once it had been saved once. See the matching
    fix in profile_analyzer.analyze_profile and docs/RECOMMENDATION_LOGIC.md.

    When False (caller omitted student_profile entirely, e.g. a bare `{}`
    request), there is nothing new to persist, so this is a no-op — the
    stored profile already has everything and this call is read-only.
    """
    if not student_profile_provided:
        return
    rp = request.student_profile
    profile.interests = list(dict.fromkeys(rp.interests))
    profile.career_goal = rp.career_goals[0] if rp.career_goals else ""
    profile.skills = list(dict.fromkeys(rp.skills))
    profile.completed_courses = list(dict.fromkeys(rp.completed_courses))
    profile.preferred_domains = list(dict.fromkeys(rp.preferred_domains))
    profile.career_preference = rp.career_preference
    profile.current_basket = rp.current_basket
    profile.raw_intent_text = rp.free_text
    if rp.semester:
        profile.semester = rp.semester
    db.commit()


def _build_item(elective: Elective, analyzed, elective_slot: str | None, career_goals_raw: list[str]) -> RecommendationItem:
    scored = score_elective(
        interest_tags=analyzed.interest_tags,
        custom_interest_terms=analyzed.custom_interest_terms,
        career_tags=analyzed.career_tags,
        skills=analyzed.skills,
        completed_courses=analyzed.completed_courses,
        elective_slot=elective_slot,
        elective_interest_tags=elective.interest_tags,
        elective_career_tags=elective.career_tags,
        elective_topics=elective.topics,
        elective_title=elective.title,
        elective_description=elective.description,
        elective_syllabus_outline=elective.syllabus_outline,
        elective_prerequisites=elective.prerequisites,
        elective_category=elective.category,
    )
    texts = build_recommendation_texts(
        course_title=elective.title,
        scored=scored,
        career_goals_raw=career_goals_raw,
        completed_courses=analyzed.completed_courses,
        elective_slot=elective_slot,
        elective_category=elective.category,
        elective_basket=elective.basket,
        current_basket=analyzed.current_basket,
        elective_description=elective.description,
        elective_syllabus_outline=elective.syllabus_outline,
        elective_prerequisites=elective.prerequisites,
    )

    return RecommendationItem(
        course_code=elective.code,
        course_name=elective.title,
        elective=ElectiveOut.model_validate(elective),
        match_percentage=scored.match_percentage,
        score_breakdown=ScoreBreakdownOut(
            components=[
                ScoreComponentOut(key=c.key, label=c.label, earned=c.earned, max=c.max) for c in scored.components
            ],
            total=scored.match_percentage,
        ),
        matched_interests=scored.matched_interests,
        matched_career_goals=scored.matched_career_tags,
        matched_skills=scored.matched_skills,
        matched_syllabus_topics=list(texts["matched_syllabus_lines"]),
        prerequisite_checks=[
            PrerequisiteCheckOut(name=c.name, satisfied=c.satisfied) for c in scored.prerequisite_checks
        ],
        why_this_matches=str(texts["why_this_matches"]),
        career_relevance=str(texts["career_relevance"]),
        syllabus_alignment=str(texts["syllabus_alignment"]),
        skill_alignment=str(texts["skill_alignment"]),
        academic_context=str(texts["academic_context"]),
        prerequisite_context=str(texts["prerequisite_context"]),
        explanation=str(texts["explanation"]),
    )


def generate_recommendations(
    db: Session, user: User, request: RecommendationRequest, student_profile_provided: bool = True
) -> RecommendationResponse:
    profile = user.profile
    analyzed = analyze_profile(request.student_profile, profile, student_profile_provided)
    elective_slot = normalize_elective_slot(request.elective_slot)
    if student_profile_provided:
        career_goals_raw = list(dict.fromkeys(v for v in request.student_profile.career_goals if v))
    else:
        career_goals_raw = request.student_profile.career_goals or (
            [profile.career_goal] if profile.career_goal else []
        )

    _persist_profile_updates(profile, request, db, student_profile_provided)

    base_query = db.query(Elective)
    if analyzed.branch:
        # Only the student's own branch's electives, plus open/generic
        # electives any branch can take (mirrors routes/electives.py).
        base_query = base_query.filter(Elective.department.in_([analyzed.branch, OPEN_ELECTIVE_DEPARTMENT]))

    # Available baskets are computed before the slot/basket-lock filters
    # below, so the response can tell the student what they *could* commit
    # to even while showing results narrowed to what they already picked.
    available_baskets = sorted(
        b for (b,) in base_query.with_entities(Elective.basket).distinct().all() if b
    )

    query = base_query.options(joinedload(Elective.faculty))

    if elective_slot:
        # Curriculum-slot eligibility: only recommend electives that
        # actually belong to the slot the student is choosing from this
        # term. This uses Elective.category (Elective I-IV / Generic
        # Elective), which was sourced from the official CSE/COE scheme
        # documents at seed time — see seed_data.py.
        query = query.filter(Elective.category == elective_slot)

    if analyzed.current_basket:
        # Basket lock: a student takes Elective I-IV from ONE EFB basket
        # only (see CODE_TO_BASKET in seed_data.py) — once committed, other
        # baskets' courses are not real options for their remaining slots.
        # Open/generic electives are a separate university-wide category
        # and are exempt from this lock.
        query = query.filter(
            or_(
                Elective.department == OPEN_ELECTIVE_DEPARTMENT,
                Elective.basket == analyzed.current_basket,
            )
        )

    electives = _dedupe_by_code(query.all())

    # Basket-level recommendations are computed independently of the
    # slot/basket-lock filters above — "which basket should I commit to"
    # is a slot-agnostic question that needs to see all four member
    # courses regardless of which single slot the student might also be
    # browsing. elective_slot=None here so Academic Fit's slot component
    # stays neutral rather than penalizing a basket for slots not asked
    # about.
    basket_pool_query = base_query.options(joinedload(Elective.faculty)).filter(Elective.basket != "")
    basket_items = [
        _build_item(e, analyzed, None, career_goals_raw) for e in _dedupe_by_code(basket_pool_query.all())
    ]
    all_baskets = build_basket_recommendations(basket_items)

    if analyzed.current_basket:
        # Already committed — nothing left to recommend a basket *for*.
        # Surface their own basket's current standing instead.
        primary_basket = next((b for b in all_baskets if b.basket_name == analyzed.current_basket), None)
        alternative_baskets = []
    else:
        primary_basket = all_baskets[0] if all_baskets else None
        alternative_baskets = all_baskets[1:4]

    items = [_build_item(e, analyzed, elective_slot, career_goals_raw) for e in electives]
    # Primary sort: match_percentage. Tie-break: total pieces of genuine
    # matched evidence (interests + career tags + skills + syllabus lines)
    # — without this, courses tied on the numeric score fall back to
    # arbitrary DB row order, which can silently bury a course with real,
    # specific evidence behind several with none at all (e.g. a handful of
    # unrelated electives that all tie at a bare "no data" floor score).
    items.sort(
        key=lambda i: (
            i.match_percentage,
            len(i.matched_interests) + len(i.matched_career_goals) + len(i.matched_skills) + len(i.matched_syllabus_topics),
        ),
        reverse=True,
    )

    primary = items[0] if items else None
    alternatives = items[1:6]
    all_eligible = [
        AllEligibleItem(
            **item.model_dump(),
            domain=item.elective.basket or item.elective.category,
            short_reason=item.why_this_matches,
        )
        for item in items
    ]

    branch_warning = None
    if not analyzed.branch:
        # See RecommendationResponse.branch_warning's docstring — without a
        # branch on file, the department filter above never ran, so results
        # blend multiple departments' catalogues together as if every
        # course were equally open to this student, which it may not be.
        branch_warning = (
            "Your profile doesn't have a branch set yet, so these results include electives from every "
            "department's catalogue — some may not actually be offered to your program. Set your branch "
            "in your profile for results narrowed to what you're actually eligible for."
        )

    return RecommendationResponse(
        # Custom (non-canonical) interest terms are included here too — not
        # just canonical tags — so the "Elective Advisor understood: ..."
        # UI actually shows every interest that was used, including custom
        # ones matched literally against course text. Omitting them would
        # make a student think a custom interest they typed was silently
        # ignored, when it was in fact scored (see scoring_engine.score_elective).
        interpreted_interests=[*analyzed.interest_tags, *analyzed.custom_interest_terms],
        interpreted_career_goals=analyzed.career_tags,
        elective_slot=elective_slot,
        current_basket=analyzed.current_basket or None,
        available_baskets=available_baskets,
        primary_basket=_basket_out(primary_basket) if primary_basket else None,
        alternative_baskets=[_basket_out(b) for b in alternative_baskets],
        all_baskets=[_basket_out(b) for b in all_baskets],
        primary_recommendation=primary,
        alternatives=alternatives,
        all_eligible_courses=all_eligible,
        weights=SCORE_WEIGHTS,
        branch_warning=branch_warning,
    )
