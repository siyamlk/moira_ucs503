from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class SlotBooking(Base):
    __tablename__ = "slot_bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    faculty_schedule_id: Mapped[int] = mapped_column(
        ForeignKey("faculty_schedules.id"), nullable=False
    )
    # "booked" | "cancelled". A cancelled row is kept, not deleted, so a
    # slot's booking history stays auditable; only a "booked" row blocks
    # the slot for other students.
    status: Mapped[str] = mapped_column(String(20), default="booked")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    student: Mapped["User"] = relationship(back_populates="bookings")
    schedule: Mapped["FacultySchedule"] = relationship(back_populates="bookings")
