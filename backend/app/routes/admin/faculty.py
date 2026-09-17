from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.core.dependencies import get_current_admin_user
from app.database.connection import get_db
from app.models.elective import Elective
from app.models.faculty import Faculty
from app.models.user import User
from app.schemas.admin import AdminFacultyCreate, AdminFacultyOut, AdminFacultyUpdate
from app.services.audit_service import record_audit

router = APIRouter(prefix="/api/admin/faculty", tags=["admin-faculty"])


@router.get("", response_model=list[AdminFacultyOut])
def list_faculty(
    search: str | None = None,
    department: str | None = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> list[AdminFacultyOut]:
    query = db.query(Faculty).options(joinedload(Faculty.schedules))
    if department:
        query = query.filter(Faculty.department == department)
    if search:
        like = f"%{search}%"
        query = query.filter(or_(Faculty.name.ilike(like), Faculty.ref_code.ilike(like)))
    faculty = query.order_by(Faculty.name).all()
    return [AdminFacultyOut.model_validate(f) for f in faculty]


@router.post("", response_model=AdminFacultyOut, status_code=status.HTTP_201_CREATED)
def create_faculty(
    payload: AdminFacultyCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> AdminFacultyOut:
    if db.query(Faculty).filter(Faculty.ref_code == payload.ref_code).first():
        raise HTTPException(status_code=400, detail="A faculty member with this ref_code already exists")
    faculty = Faculty(**payload.model_dump())
    db.add(faculty)
    db.flush()
    record_audit(db, current_user.id, "create", "faculty", faculty.id, {"ref_code": faculty.ref_code})
    db.commit()
    db.refresh(faculty)
    return AdminFacultyOut.model_validate(faculty)


@router.put("/{faculty_id}", response_model=AdminFacultyOut)
def update_faculty(
    faculty_id: int,
    payload: AdminFacultyUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> AdminFacultyOut:
    faculty = db.query(Faculty).filter(Faculty.id == faculty_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty member not found")

    updates = payload.model_dump(exclude_unset=True)
    if "ref_code" in updates:
        clash = (
            db.query(Faculty)
            .filter(Faculty.ref_code == updates["ref_code"], Faculty.id != faculty_id)
            .first()
        )
        if clash:
            raise HTTPException(status_code=400, detail="A faculty member with this ref_code already exists")

    for field, value in updates.items():
        setattr(faculty, field, value)
    record_audit(db, current_user.id, "update", "faculty", faculty.id, {"fields": list(updates.keys())})
    db.commit()
    db.refresh(faculty)
    return AdminFacultyOut.model_validate(faculty)


@router.delete("/{faculty_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_faculty(
    faculty_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> None:
    faculty = db.query(Faculty).filter(Faculty.id == faculty_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty member not found")

    assigned_electives = db.query(Elective).filter(Elective.faculty_id == faculty_id).count()
    if assigned_electives > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"{assigned_electives} elective(s) are assigned to this faculty member; "
                "reassign or clear them first"
            ),
        )

    record_audit(db, current_user.id, "delete", "faculty", faculty.id, {"ref_code": faculty.ref_code})
    db.delete(faculty)
    db.commit()
