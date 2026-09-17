from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin_user
from app.database.connection import get_db
from app.models.academic_config import AcademicConfig
from app.models.user import User
from app.schemas.admin import AcademicConfigOut, AcademicConfigUpdate
from app.services.academic_config_service import RECOMMENDATION_WEIGHTS_KEY, weights_are_valid
from app.services.audit_service import record_audit

router = APIRouter(prefix="/api/admin/config", tags=["admin-config"])


@router.get("", response_model=list[AcademicConfigOut])
def list_config(
    current_user: User = Depends(get_current_admin_user), db: Session = Depends(get_db)
) -> list[AcademicConfigOut]:
    rows = db.query(AcademicConfig).order_by(AcademicConfig.key).all()
    return [AcademicConfigOut.model_validate(r) for r in rows]


@router.get("/{key}", response_model=AcademicConfigOut)
def get_config(
    key: str, current_user: User = Depends(get_current_admin_user), db: Session = Depends(get_db)
) -> AcademicConfigOut:
    row = db.query(AcademicConfig).filter(AcademicConfig.key == key).first()
    if not row:
        raise HTTPException(status_code=404, detail="Configuration key not found")
    return AcademicConfigOut.model_validate(row)


@router.put("/{key}", response_model=AcademicConfigOut)
def update_config(
    key: str,
    payload: AcademicConfigUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> AcademicConfigOut:
    if key == RECOMMENDATION_WEIGHTS_KEY and not weights_are_valid(payload.value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "recommendation_weights must be an object with exactly the interest/career/syllabus/"
                "skill/academic/prerequisite keys, integer values, summing to 100"
            ),
        )

    row = db.query(AcademicConfig).filter(AcademicConfig.key == key).first()
    if not row:
        row = AcademicConfig(key=key, value=payload.value, description=payload.description or "")
        db.add(row)
    else:
        row.value = payload.value
        if payload.description is not None:
            row.description = payload.description
    row.updated_by = current_user.id
    db.flush()
    record_audit(db, current_user.id, "update", "academic_config", row.id, {"key": key})
    db.commit()
    db.refresh(row)
    return AcademicConfigOut.model_validate(row)
