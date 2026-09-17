from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin_user
from app.database.connection import get_db
from app.models.faculty import Faculty
from app.models.faculty_schedule import FacultySchedule
from app.models.user import User
from app.schemas.admin import AdminScheduleCreate, AdminScheduleOut, AdminScheduleUpdate
from app.services.audit_service import record_audit

router = APIRouter(prefix="/api/admin/schedules", tags=["admin-schedules"])


def _assert_faculty_exists(db: Session, faculty_id: int) -> None:
    if not db.query(Faculty).filter(Faculty.id == faculty_id).first():
        raise HTTPException(status_code=400, detail="faculty_id does not refer to an existing faculty member")


@router.get("", response_model=list[AdminScheduleOut])
def list_schedules(
    faculty_id: int | None = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> list[AdminScheduleOut]:
    query = db.query(FacultySchedule)
    if faculty_id is not None:
        query = query.filter(FacultySchedule.faculty_id == faculty_id)
    schedules = query.order_by(FacultySchedule.faculty_id, FacultySchedule.day).all()
    return [AdminScheduleOut.model_validate(s) for s in schedules]


@router.post("", response_model=AdminScheduleOut, status_code=status.HTTP_201_CREATED)
def create_schedule(
    payload: AdminScheduleCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> AdminScheduleOut:
    _assert_faculty_exists(db, payload.faculty_id)
    schedule = FacultySchedule(**payload.model_dump())
    db.add(schedule)
    db.flush()
    record_audit(
        db, current_user.id, "create", "faculty_schedule", schedule.id, {"faculty_id": schedule.faculty_id}
    )
    db.commit()
    db.refresh(schedule)
    return AdminScheduleOut.model_validate(schedule)


@router.put("/{schedule_id}", response_model=AdminScheduleOut)
def update_schedule(
    schedule_id: int,
    payload: AdminScheduleUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> AdminScheduleOut:
    schedule = db.query(FacultySchedule).filter(FacultySchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule entry not found")

    updates = payload.model_dump(exclude_unset=True)
    if "faculty_id" in updates:
        _assert_faculty_exists(db, updates["faculty_id"])

    for field, value in updates.items():
        setattr(schedule, field, value)
    record_audit(
        db, current_user.id, "update", "faculty_schedule", schedule.id, {"fields": list(updates.keys())}
    )
    db.commit()
    db.refresh(schedule)
    return AdminScheduleOut.model_validate(schedule)


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> None:
    schedule = db.query(FacultySchedule).filter(FacultySchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule entry not found")
    record_audit(db, current_user.id, "delete", "faculty_schedule", schedule.id, None)
    db.delete(schedule)
    db.commit()
