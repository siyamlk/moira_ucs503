from sqlalchemy import JSON, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Elective(Base):
    __tablename__ = "electives"
    __table_args__ = (UniqueConstraint("code", "department", name="uq_elective_code_department"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    # Course codes are drawn from a shared university-wide PEC/OEC pool, so the
    # same code (e.g. UCS531) can legitimately appear under multiple
    # departments/branches — uniqueness is (code, department), not code alone.
    code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    department: Mapped[str] = mapped_column(String(120), default="")
    credits: Mapped[float] = mapped_column(Float, default=4.0)
    prerequisites: Mapped[str] = mapped_column(String(200), default="")
    description: Mapped[str] = mapped_column(String(1000), default="")
    category: Mapped[str] = mapped_column(String(60), default="")  # "Elective I".."Elective IV" / "Generic Elective"
    # The named EFB track this course belongs to (e.g. "Data Science",
    # "DevOps and Continuous Delivery"). A student commits to ONE basket
    # and takes Elective I-IV from within it only — they cannot mix
    # courses from different baskets across those four slots. Empty for
    # generic/open electives (no basket concept) and for the handful of
    # CSE/COE electives not grouped under a named EFB basket in the
    # source catalogue. See seed_data.py CODE_TO_BASKET.
    basket: Mapped[str] = mapped_column(String(80), default="")
    topics: Mapped[list[str]] = mapped_column(JSON, default=list)
    # Real unit/module headers from the official EFB syllabus document, not
    # tags — shown verbatim in the UI as "Syllabus Outline" (see
    # backend/app/seed/data/electives_efb_details.csv).
    syllabus_outline: Mapped[list[str]] = mapped_column(JSON, default=list)
    interest_tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    career_tags: Mapped[list[str]] = mapped_column(JSON, default=list)

    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculty.id"), nullable=True)
    faculty: Mapped["Faculty"] = relationship(back_populates="electives")
