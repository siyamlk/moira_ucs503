"""Weighted, transparent scoring engine for the elective recommendation system.

Every match_percentage this module produces is the literal sum of six
independently-computed, auditable components (see SCORE_WEIGHTS below) —
there is no random number and no per-course hardcoded percentage anywhere
in this codebase. Given the same student profile and the same course data,
`score_elective` always returns the same result.

Each component is a ratio (0.0-1.0) between something the student stated
and something actually present on the Elective record, multiplied by that
component's weight and rounded to an integer. Because every ratio is
clamped to [0, 1], every earned component is guaranteed to fall within
[0, its own weight] — so the six components can never sum past 100.
"""

from dataclasses import dataclass, field

from app.recommendation.profile_analyzer import normalize_elective_slot
from app.recommendation.syllabus_matcher import find_matched_syllabus_lines
from app.services.recommendation_service import text_contains

# Configurable in one place. Change these to retune the whole system —
# every score is recomputed live from these weights on every request,
# nothing is cached or precomputed per-course. Must sum to 100.
SCORE_WEIGHTS: dict[str, int] = {
    "interest": 25,
    "career": 25,
    "syllabus": 20,
    "skill": 15,
    "academic": 10,
    "prerequisite": 5,
}
assert sum(SCORE_WEIGHTS.values()) == 100, "SCORE_WEIGHTS must sum to 100"

COMPONENT_LABELS: dict[str, str] = {
    "interest": "Interest Alignment",
    "career": "Career Goal Alignment",
    "syllabus": "Syllabus Alignment",
    "skill": "Skill Alignment",
    "academic": "Academic Fit",
    "prerequisite": "Prerequisite Compatibility",
}


@dataclass
class ScoreComponent:
    key: str
    label: str
    earned: int
    max: int


@dataclass
class PrerequisiteCheck:
    name: str
    satisfied: bool


@dataclass
class ScoredMatch:
    match_percentage: int
    components: list[ScoreComponent]
    matched_interests: list[str] = field(default_factory=list)
    matched_career_tags: list[str] = field(default_factory=list)
    matched_topics: list[str] = field(default_factory=list)
    matched_skills: list[str] = field(default_factory=list)
    matched_syllabus_lines: list[str] = field(default_factory=list)
    prerequisite_checks: list[PrerequisiteCheck] = field(default_factory=list)
    slot_matched: bool | None = None  # None = student didn't specify a slot


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _earn(component_key: str, ratio: float, weights: dict[str, int]) -> int:
    ratio = max(0.0, min(1.0, ratio))
    # Round-half-up rather than Python's banker's-rounding round(), so
    # e.g. 2.5 -> 3 consistently instead of 2 — the intuitive behavior a
    # student reading "X/Y" expects.
    return int(weights[component_key] * ratio + 0.5)


def score_elective(
    *,
    interest_tags: list[str],
    career_tags: list[str],
    skills: list[str],
    completed_courses: list[str],
    elective_slot: str | None,
    elective_interest_tags: list[str],
    elective_career_tags: list[str],
    elective_topics: list[str],
    elective_title: str,
    elective_description: str,
    elective_syllabus_outline: list[str],
    elective_prerequisites: str,
    elective_category: str,
    custom_interest_terms: list[str] | None = None,
    weights: dict[str, int] | None = None,
) -> ScoredMatch:
    # Defaults to the hardcoded SCORE_WEIGHTS so every existing caller (and
    # test) that doesn't pass weights keeps behaving identically. Admin-
    # configured overrides flow in only where the caller explicitly loads
    # them (see app.services.academic_config_service.get_recommendation_weights).
    weights = weights or SCORE_WEIGHTS
    custom_interest_terms = custom_interest_terms or []
    interest_set = set(interest_tags)
    career_set = set(career_tags)

    # combined_text is also needed below for skill matching — compute once.
    combined_text = f"{elective_title} {elective_description} {' '.join(elective_syllabus_outline)}".lower()

    # --- Interest alignment: student interest tags vs this elective's tags,
    # PLUS custom interest text (typed by the student, not one of our fixed
    # canonical tags — e.g. "Sustainable Computing") matched literally
    # against this course's title/description/syllabus. Without this, any
    # interest that doesn't happen to match one of our ~25 preset tags had
    # ZERO effect on scoring — it would still render as an accepted chip in
    # the UI, quietly doing nothing, which is exactly the kind of thing that
    # misleads a student trusting the match percentage. ---
    matched_interests = sorted(interest_set & set(elective_interest_tags))
    normalized_custom_interests = [t.strip().lower() for t in custom_interest_terms if t.strip()]
    matched_custom_interests = [t for t in normalized_custom_interests if text_contains(combined_text, t)]
    interest_denominator = len(interest_set) + len(normalized_custom_interests)
    interest_numerator = len(matched_interests) + len(matched_custom_interests)
    interest_earned = _earn("interest", _ratio(interest_numerator, interest_denominator), weights)

    # --- Career alignment: proportional, not all-or-nothing. A course that
    # matches only one of the student's several career-goal tags shouldn't
    # score the same as one matching all of them — that would let a
    # tangential single-tag overlap (e.g. an AR/VR course that briefly
    # mentions computer vision) earn full career credit, on par with a
    # course genuinely centered on that career path. ---
    matched_career = sorted(career_set & set(elective_career_tags))
    career_earned = _earn("career", _ratio(len(matched_career), len(career_set)), weights)

    # --- Syllabus alignment: primarily real evidence from the actual EFB
    # unit headers, with a flat (not ratio-based) floor when a course is
    # genuinely tagged relevant but its real text doesn't spell it out.
    #
    # An earlier version divided by *this course's own* topic count, which
    # backfired: a narrowly-tagged course (1 topic total) would hit a
    # "perfect" ratio trivially, while a richly-tagged course covering
    # MORE genuine ground (e.g. a Robotics-basket course that also covers
    # Computer Vision) scored *lower* for the same match, simply for
    # having more topics in its denominator — rewarding thin tagging over
    # substantive relevance. A flat floor has no such bias: it doesn't
    # matter how many other things a course also covers.
    #
    # The floor also fixes the opposite failure mode a pure-line-match
    # design has: real unit-header wording ("HTML and CSS", "JavaScript")
    # can legitimately never spell out a broader theme the course is
    # obviously about (e.g. a UI/UX course whose units are named after
    # specific technologies) — using line-matching alone would then
    # unfairly zero out that course's most important signal. ---
    TAG_RELEVANT_FLOOR = 0.35
    matched_topics = sorted(interest_set & set(elective_topics))
    baseline_ratio = TAG_RELEVANT_FLOOR if matched_topics else 0.0
    if elective_syllabus_outline:
        # Custom interest terms are literal text (like skills), not
        # canonical tags — folded into the skills argument here only, so
        # a real syllabus line can be cited as evidence for them too.
        matched_syllabus_lines = find_matched_syllabus_lines(
            interest_tags, [*skills, *custom_interest_terms], elective_syllabus_outline
        )
        line_ratio = _ratio(len(matched_syllabus_lines), len(elective_syllabus_outline))
        # Real evidence, when it clears the floor, earns credit above it;
        # weak/no real evidence never scores *below* the tag-relevant
        # floor — finding some evidence should never be worse than
        # finding none. (line_ratio can be positive from a skill-keyword
        # match alone even with no interest-tag relevance, which is
        # correctly still credited via this max().)
        syllabus_ratio = max(line_ratio, baseline_ratio)
    else:
        matched_syllabus_lines = []
        syllabus_ratio = baseline_ratio
    syllabus_earned = _earn("syllabus", syllabus_ratio, weights)

    # --- Skill alignment: literal skill keywords the student typed vs the
    # actual course title/description/syllabus text (not the canonical tag
    # vocabulary — skills are specific technologies, e.g. "Docker") ---
    normalized_skills = [s.strip().lower() for s in skills if s.strip()]
    matched_skills = [s for s in normalized_skills if text_contains(combined_text, s)]
    skill_earned = _earn("skill", _ratio(len(matched_skills), len(normalized_skills)), weights)

    # --- Academic fit: does this elective sit in the slot the student is
    # actually choosing from this term, plus any overlap between completed
    # coursework and this elective's own stated prerequisites/description.
    # NOTE: without the CSE/COE curriculum scheme documents (semester-by-
    # semester subject lists), this component can only use what's on the
    # Elective record itself (its basket/category) — it cannot validate a
    # full curriculum prerequisite chain. See docs/RECOMMENDATION_LOGIC.md.
    slot_matched: bool | None = None
    if elective_slot:
        slot_matched = normalize_elective_slot(elective_category) == normalize_elective_slot(elective_slot)
        slot_ratio = 1.0 if slot_matched else 0.0
    else:
        slot_ratio = 0.5  # neutral — student didn't specify a slot to filter by

    normalized_completed = [c.strip().lower() for c in completed_courses if c.strip()]
    prereq_names = [p.strip() for p in elective_prerequisites.split(";") if p.strip()]
    coursework_hits = sum(
        1
        for c in normalized_completed
        if any(c in p.lower() or p.lower() in c for p in prereq_names) or c in elective_description.lower()
    )
    coursework_ratio = _ratio(min(coursework_hits, 3), 3) if normalized_completed else 0.0
    academic_earned = _earn("academic", (slot_ratio + coursework_ratio) / 2, weights)

    # --- Prerequisite compatibility: has the student completed what this
    # elective's own "Recommended Prerequisites" line (sourced from the EFB
    # catalogue) actually asks for? Electives with no stated prerequisite
    # are fully compatible by definition. ---
    prerequisite_checks: list[PrerequisiteCheck] = []
    if not prereq_names:
        prereq_ratio = 1.0
    else:
        satisfied = 0
        for name in prereq_names:
            ok = any(name.lower() in c or c in name.lower() for c in normalized_completed)
            prerequisite_checks.append(PrerequisiteCheck(name=name, satisfied=ok))
            satisfied += int(ok)
        prereq_ratio = _ratio(satisfied, len(prereq_names))
    prerequisite_earned = _earn("prerequisite", prereq_ratio, weights)

    components = [
        ScoreComponent("interest", COMPONENT_LABELS["interest"], interest_earned, weights["interest"]),
        ScoreComponent("career", COMPONENT_LABELS["career"], career_earned, weights["career"]),
        ScoreComponent("syllabus", COMPONENT_LABELS["syllabus"], syllabus_earned, weights["syllabus"]),
        ScoreComponent("skill", COMPONENT_LABELS["skill"], skill_earned, weights["skill"]),
        ScoreComponent("academic", COMPONENT_LABELS["academic"], academic_earned, weights["academic"]),
        ScoreComponent(
            "prerequisite", COMPONENT_LABELS["prerequisite"], prerequisite_earned, weights["prerequisite"]
        ),
    ]
    match_percentage = min(100, sum(c.earned for c in components))

    return ScoredMatch(
        match_percentage=match_percentage,
        components=components,
        # Custom (non-canonical) interest terms that literally matched this
        # course's text are genuinely "matched interests" from the
        # student's perspective — surfaced the same way as canonical tag
        # matches in explanations/basket summaries, not as a separate
        # never-shown category.
        matched_interests=sorted({*matched_interests, *matched_custom_interests}),
        matched_career_tags=matched_career,
        matched_topics=matched_topics,
        matched_skills=matched_skills,
        matched_syllabus_lines=matched_syllabus_lines,
        prerequisite_checks=prerequisite_checks,
        slot_matched=slot_matched,
    )
