from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.faculty import ScheduleOut


class AdminElectiveCreate(BaseModel):
    code: str = Field(min_length=1, max_length=20)
    title: str = Field(min_length=1, max_length=200)
    department: str = Field(default="", max_length=120)
    credits: float = Field(default=4.0, ge=0)
    prerequisites: str = Field(default="", max_length=200)
    description: str = Field(default="", max_length=1000)
    category: str = Field(default="", max_length=60)
    basket: str = Field(default="", max_length=80)
    topics: list[str] = Field(default_factory=list)
    syllabus_outline: list[str] = Field(default_factory=list)
    interest_tags: list[str] = Field(default_factory=list)
    career_tags: list[str] = Field(default_factory=list)
    faculty_id: int | None = None


class AdminElectiveUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=20)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    department: str | None = Field(default=None, max_length=120)
    credits: float | None = Field(default=None, ge=0)
    prerequisites: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    category: str | None = Field(default=None, max_length=60)
    basket: str | None = Field(default=None, max_length=80)
    topics: list[str] | None = None
    syllabus_outline: list[str] | None = None
    interest_tags: list[str] | None = None
    career_tags: list[str] | None = None
    faculty_id: int | None = None


class AdminElectiveOut(BaseModel):
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
    syllabus_outline: list[str]
    interest_tags: list[str]
    career_tags: list[str]
    faculty_id: int | None

    model_config = {"from_attributes": True}


class AdminFacultyCreate(BaseModel):
    ref_code: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=120)
    title: str = Field(default="", max_length=120)
    department: str = Field(default="Department of Computer Science", max_length=120)
    specialization: str = Field(default="", max_length=300)
    research_interests: list[str] = Field(default_factory=list)
    office_location: str = Field(default="", max_length=120)
    email: str = Field(default="", max_length=180)
    photo_url: str = Field(default="", max_length=500)
    profile_url: str = Field(default="", max_length=500)


class AdminFacultyUpdate(BaseModel):
    ref_code: str | None = Field(default=None, min_length=1, max_length=20)
    name: str | None = Field(default=None, min_length=1, max_length=120)
    title: str | None = Field(default=None, max_length=120)
    department: str | None = Field(default=None, max_length=120)
    specialization: str | None = Field(default=None, max_length=300)
    research_interests: list[str] | None = None
    office_location: str | None = Field(default=None, max_length=120)
    email: str | None = Field(default=None, max_length=180)
    photo_url: str | None = Field(default=None, max_length=500)
    profile_url: str | None = Field(default=None, max_length=500)


class AdminFacultyOut(BaseModel):
    id: int
    ref_code: str
    name: str
    title: str
    department: str
    specialization: str
    research_interests: list[str]
    office_location: str
    email: str
    photo_url: str
    profile_url: str
    schedules: list[ScheduleOut] = []

    model_config = {"from_attributes": True}


class AdminScheduleCreate(BaseModel):
    faculty_id: int
    day: str = Field(min_length=1, max_length=20)
    start_time: str = Field(min_length=1, max_length=10)
    end_time: str = Field(min_length=1, max_length=10)
    room: str = Field(default="", max_length=60)
    note: str = Field(default="Office Hours", max_length=160)
    semester: str = Field(default="", max_length=40)


class AdminScheduleUpdate(BaseModel):
    faculty_id: int | None = None
    day: str | None = Field(default=None, min_length=1, max_length=20)
    start_time: str | None = Field(default=None, min_length=1, max_length=10)
    end_time: str | None = Field(default=None, min_length=1, max_length=10)
    room: str | None = Field(default=None, max_length=60)
    note: str | None = Field(default=None, max_length=160)
    semester: str | None = Field(default=None, max_length=40)


class AdminScheduleOut(BaseModel):
    id: int
    faculty_id: int
    day: str
    start_time: str
    end_time: str
    room: str
    note: str
    semester: str

    model_config = {"from_attributes": True}


class AcademicConfigUpdate(BaseModel):
    value: Any
    description: str | None = Field(default=None, max_length=300)


class AcademicConfigOut(BaseModel):
    id: int
    key: str
    value: Any
    description: str
    updated_at: datetime
    updated_by: int | None

    model_config = {"from_attributes": True}


class AuditLogOut(BaseModel):
    id: int
    admin_id: int | None
    action: str
    entity_type: str
    entity_id: int | None
    details: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DashboardOut(BaseModel):
    total_electives: int
    total_faculty: int
    total_baskets: int
    total_categories: int
    recent_activity: list[AuditLogOut]
