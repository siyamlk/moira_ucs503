from pydantic import BaseModel, Field

from app.schemas.elective import ElectiveOut


class StudentProfileIn(BaseModel):
    """Any field left empty/omitted falls back to what's already stored on
    the student's profile (see profile_analyzer.analyze_profile) — the
    student never has to repeat information AdvisorAI already has."""

    program: str = ""
    semester: int | None = Field(default=None, ge=1, le=12)
    interests: list[str] = Field(default_factory=list)
    career_goals: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    completed_courses: list[str] = Field(default_factory=list)
    preferred_domains: list[str] = Field(default_factory=list)
    career_preference: str = ""
    free_text: str = Field(default="", max_length=2000)
    # The EFB basket already committed to (e.g. "Data Science"), if any —
    # leave empty when picking Elective I for the first time. See
    # StudentProfile.current_basket.
    current_basket: str = ""


class RecommendationRequest(BaseModel):
    student_profile: StudentProfileIn = Field(default_factory=StudentProfileIn)
    elective_slot: str | None = None


class ScoreComponentOut(BaseModel):
    key: str
    label: str
    earned: int
    max: int


class ScoreBreakdownOut(BaseModel):
    components: list[ScoreComponentOut]
    total: int
    max_total: int = 100


class PrerequisiteCheckOut(BaseModel):
    name: str
    satisfied: bool


class RecommendationItem(BaseModel):
    course_code: str
    course_name: str
    elective: ElectiveOut
    match_percentage: int
    score_breakdown: ScoreBreakdownOut
    matched_interests: list[str]
    matched_career_goals: list[str]
    matched_skills: list[str]
    matched_syllabus_topics: list[str]
    prerequisite_checks: list[PrerequisiteCheckOut]
    why_this_matches: str
    career_relevance: str
    syllabus_alignment: str
    skill_alignment: str
    academic_context: str
    prerequisite_context: str
    explanation: str


class BasketRecommendationOut(BaseModel):
    """A whole Elective Focus Basket (e.g. "Data Science"), aggregating
    its member Elective I-IV courses — the primary recommendation unit,
    since a student commits to one basket and takes all four electives
    from within it (see app/recommendation/basket_service.py)."""

    basket_name: str
    match_percentage: int
    electives: list[RecommendationItem]
    matched_interests: list[str]
    matched_career_goals: list[str]
    why_this_basket_matches: str


class AllEligibleItem(RecommendationItem):
    """Everything a RecommendationItem has, plus a domain/short_reason pair
    — so the "Compare Electives" feature has full score-breakdown data for
    *any* eligible course, not just the top 6 (primary + alternatives)."""

    domain: str
    short_reason: str


class RecommendationResponse(BaseModel):
    interpreted_interests: list[str]
    interpreted_career_goals: list[str]
    elective_slot: str | None
    # The EFB basket results were constrained to, if the student has
    # already committed to one (see StudentProfileIn.current_basket) —
    # null means they haven't committed yet, so all baskets are shown.
    current_basket: str | None
    available_baskets: list[str]
    # Basket-level recommendation: the primary unit a student actually
    # chooses (commit to one basket, take Elective I-IV from within it).
    # Null when the student has already committed to a basket — at that
    # point there's nothing left to recommend a basket *for*.
    primary_basket: BasketRecommendationOut | None
    alternative_baskets: list[BasketRecommendationOut]
    all_baskets: list[BasketRecommendationOut]
    # Individual-course-level view — still useful for open/generic
    # electives and the few courses not grouped under any named basket,
    # and for browsing/comparing single courses directly.
    primary_recommendation: RecommendationItem | None
    alternatives: list[RecommendationItem]
    all_eligible_courses: list[AllEligibleItem]
    weights: dict[str, int]
    # Non-null when the student's profile has no branch set: results below
    # then include courses from every department's catalogue combined
    # (some genuinely department-specific), not narrowed to what the
    # student's own program actually offers — surfaced explicitly rather
    # than silently shown as if all were equally available. See
    # docs/RECOMMENDATION_LOGIC.md.
    branch_warning: str | None = None
