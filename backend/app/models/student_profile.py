from sqlalchemy import JSON, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)

    semester: Mapped[int] = mapped_column(Integer, default=1)
    # Empty until the student sets it (no branch assumed) — must exactly match
    # an Elective.department value for branch-aware elective filtering to work.
    # See core/constants.BRANCH_DEPARTMENTS.
    branch: Mapped[str] = mapped_column(String(120), default="")
    cgpa: Mapped[float] = mapped_column(Float, default=0.0)
    credits_earned: Mapped[int] = mapped_column(Integer, default=0)
    credits_required: Mapped[int] = mapped_column(Integer, default=160)
    career_goal: Mapped[str] = mapped_column(String(160), default="")
    interests: Mapped[list[str]] = mapped_column(JSON, default=list)
    raw_intent_text: Mapped[str] = mapped_column(String(2000), default="")

    # Recommendation-engine inputs the student would otherwise have to
    # re-enter on every /api/recommendations call — persisted so a later
    # call can omit them and reuse what's on file (see
    # app/recommendation/profile_analyzer.py).
    skills: Mapped[list[str]] = mapped_column(JSON, default=list)
    completed_courses: Mapped[list[str]] = mapped_column(JSON, default=list)
    preferred_domains: Mapped[list[str]] = mapped_column(JSON, default=list)
    # Free text: e.g. "Research", "Industry", "Higher Studies", "Entrepreneurship".
    career_preference: Mapped[str] = mapped_column(String(60), default="")
    # The EFB basket (e.g. "Data Science") this student has already
    # committed to via an earlier elective pick — Elective I-IV all come
    # from one basket only, so once set, recommendations for II/III/IV are
    # constrained to it. Empty = not committed yet (picking Elective I).
    current_basket: Mapped[str] = mapped_column(String(80), default="")

    user: Mapped["User"] = relationship(back_populates="profile")
