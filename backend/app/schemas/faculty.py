from pydantic import BaseModel


class ScheduleOut(BaseModel):
    id: int
    day: str
    start_time: str
    end_time: str
    room: str
    note: str

    model_config = {"from_attributes": True}


class FacultyOut(BaseModel):
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
