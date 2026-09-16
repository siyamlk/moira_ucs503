from datetime import datetime

from pydantic import BaseModel, Field


class BacklogCreate(BaseModel):
    subject: str = Field(min_length=2, max_length=160)
    course_code: str = Field(min_length=2, max_length=20)
    credits: float = Field(gt=0, le=10)
    course_type: str = Field(default="Core Course", max_length=40)
    current_grade: str = Field(default="F", max_length=10)


class BacklogOut(BaseModel):
    id: int
    subject: str
    course_code: str
    credits: float
    course_type: str
    current_grade: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PrioritizedBacklogOut(BaseModel):
    backlog: BacklogOut
    priority_rank: int
    priority_label: str
    cgpa_impact: float
    estimated_new_cgpa: float
    explanation: str


class PrioritizeResponse(BaseModel):
    current_cgpa: float
    pending_count: int
    prioritized: list[PrioritizedBacklogOut]
