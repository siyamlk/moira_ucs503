from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class FacultySchedule(Base):
    __tablename__ = "faculty_schedules"

    id: Mapped[int] = mapped_column(primary_key=True)
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculty.id"), nullable=False)
    day: Mapped[str] = mapped_column(String(20), nullable=False)
    start_time: Mapped[str] = mapped_column(String(10), nullable=False)
    end_time: Mapped[str] = mapped_column(String(10), nullable=False)
    room: Mapped[str] = mapped_column(String(60), default="")
    note: Mapped[str] = mapped_column(String(160), default="Office Hours")
    # Free-text term this slot applies to (e.g. "Odd 2026-27"). Empty means
    # "standing/every semester" — admins are responsible for entering this,
    # nothing here is inferred or invented.
    semester: Mapped[str] = mapped_column(String(40), default="")

    faculty: Mapped["Faculty"] = relationship(back_populates="schedules")
