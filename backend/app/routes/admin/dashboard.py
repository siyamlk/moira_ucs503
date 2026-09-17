from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin_user
from app.database.connection import get_db
from app.models.audit_log import AuditLog
from app.models.elective import Elective
from app.models.faculty import Faculty
from app.models.user import User
from app.schemas.admin import AuditLogOut, DashboardOut

router = APIRouter(prefix="/api/admin", tags=["admin-dashboard"])


@router.get("/dashboard", response_model=DashboardOut)
def get_dashboard(
    current_user: User = Depends(get_current_admin_user), db: Session = Depends(get_db)
) -> DashboardOut:
    total_electives = db.query(Elective).count()
    total_faculty = db.query(Faculty).count()
    total_baskets = len({b for (b,) in db.query(Elective.basket).distinct().all() if b})
    total_categories = len({c for (c,) in db.query(Elective.category).distinct().all() if c})
    recent = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(10).all()
    return DashboardOut(
        total_electives=total_electives,
        total_faculty=total_faculty,
        total_baskets=total_baskets,
        total_categories=total_categories,
        recent_activity=[AuditLogOut.model_validate(a) for a in recent],
    )
