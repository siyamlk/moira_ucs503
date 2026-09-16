from pydantic import BaseModel, Field


class ProfileUpdate(BaseModel):
    semester: int | None = Field(default=None, ge=1, le=12)
    branch: str | None = None
    cgpa: float | None = Field(default=None, ge=0, le=10)
    credits_earned: int | None = Field(default=None, ge=0)
    credits_required: int | None = Field(default=None, ge=0)
    career_goal: str | None = None
    interests: list[str] | None = None
    raw_intent_text: str | None = None
    skills: list[str] | None = None
    completed_courses: list[str] | None = None
    preferred_domains: list[str] | None = None
    career_preference: str | None = None
    current_basket: str | None = None


class ProfileOut(BaseModel):
    id: int
    semester: int
    branch: str
    cgpa: float
    credits_earned: int
    credits_required: int
    career_goal: str
    interests: list[str]
    raw_intent_text: str
    skills: list[str]
    completed_courses: list[str]
    preferred_domains: list[str]
    career_preference: str
    current_basket: str

    model_config = {"from_attributes": True}
