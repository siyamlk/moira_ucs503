from datetime import datetime

from pydantic import BaseModel

from app.schemas.faculty import ScheduleOut


class BookingCreate(BaseModel):
    faculty_schedule_id: int


class BookingOut(BaseModel):
    id: int
    faculty_schedule_id: int
    status: str
    created_at: datetime
    schedule: ScheduleOut

    model_config = {"from_attributes": True}
