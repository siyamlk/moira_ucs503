from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class AcademicConfig(Base):
    """Generic admin-managed key/value store for academic rules the advisory
    engines consume (e.g. "recommendation_weights", "elective_categories").
    Keeping this generic (rather than one column per setting) lets new
    configurable rules be added later without a schema change."""

    __tablename__ = "academic_config"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    value: Mapped[dict | list] = mapped_column(JSON, nullable=False)
    description: Mapped[str] = mapped_column(String(300), default="")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
