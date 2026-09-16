from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Faculty(Base):
    __tablename__ = "faculty"

    id: Mapped[int] = mapped_column(primary_key=True)
    ref_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    title: Mapped[str] = mapped_column(String(120), default="")
    department: Mapped[str] = mapped_column(String(120), default="Department of Computer Science")
    specialization: Mapped[str] = mapped_column(String(300), default="")
    research_interests: Mapped[list[str]] = mapped_column(JSON, default=list)
    office_location: Mapped[str] = mapped_column(String(120), default="")
    email: Mapped[str] = mapped_column(String(180), default="")
    photo_url: Mapped[str] = mapped_column(String(500), default="")
    profile_url: Mapped[str] = mapped_column(String(500), default="")

    schedules: Mapped[list["FacultySchedule"]] = relationship(
        back_populates="faculty", cascade="all, delete-orphan"
    )
    electives: Mapped[list["Elective"]] = relationship(back_populates="faculty")
