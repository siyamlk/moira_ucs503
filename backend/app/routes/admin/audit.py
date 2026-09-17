from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin_user
from app.database.connection import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.admin import AuditLogOut

router = APIRouter(prefix="/api/admin/audit-log", tags=["admin-audit"])


@router.get("", response_model=list[AuditLogOut])
def list_audit_log(
    limit: int = 50,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> list[AuditLogOut]:
    limit = max(1, min(limit, 200))
    rows = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [AuditLogOut.model_validate(r) for r in rows]
