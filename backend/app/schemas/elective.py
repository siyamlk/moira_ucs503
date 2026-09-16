from pydantic import BaseModel, Field

from app.schemas.faculty import FacultyOut


class ElectiveOut(BaseModel):
    id: int
    code: str
    title: str
    department: str
    credits: float
    prerequisites: str
    description: str
    category: str
    basket: str
    topics: list[str]
    syllabus_outline: list[str] = []
    faculty: FacultyOut | None = None

    model_config = {"from_attributes": True}


class RecommendRequest(BaseModel):
    free_text: str = Field(default="", max_length=2000)
    interests: list[str] = Field(default_factory=list)
    career_goal: str = Field(default="")


class ScoreBreakdown(BaseModel):
    """The exact arithmetic behind `match_percent` — these four components
    always sum to it. Returned so the match score is auditable rather than
    an opaque number (see recommendation_service.score_elective)."""

    interest_points: float
    interest_matched: int
    interest_total: int
    career_points: float
    career_matched: bool
    topic_points: float
    topic_matched: int
    topic_total: int
    bonus_points: float


class RecommendationOut(BaseModel):
    elective: ElectiveOut
    match_percent: int
    interest_match: bool
    career_match: bool
    matched_topics: list[str]
    explanation: str
    score_breakdown: ScoreBreakdown
    suggested_faculty: list[FacultyOut] = []


class RecommendResponse(BaseModel):
    interpreted_tags: list[str]
    career_goal: str
    top_recommendation: RecommendationOut | None
    alternatives: list[RecommendationOut]
