from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Backlog(Base):
    __tablename__ = "backlogs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    subject: Mapped[str] = mapped_column(String(160), nullable=False)
    course_code: Mapped[str] = mapped_column(String(20), nullable=False)
    credits: Mapped[float] = mapped_column(Float, nullable=False)
    course_type: Mapped[str] = mapped_column(String(40), default="Core Course")
    current_grade: Mapped[str] = mapped_column(String(10), default="F")
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="backlogs")
