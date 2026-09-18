from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin_user
from app.database.connection import get_db
from app.models.elective import Elective
from app.models.faculty import Faculty
from app.models.user import User
from app.schemas.admin import AdminElectiveCreate, AdminElectiveOut, AdminElectiveUpdate
from app.services.audit_service import record_audit
from app.services.cache_service import ELECTIVES_LIST_CACHE_KEY, invalidate

router = APIRouter(prefix="/api/admin/electives", tags=["admin-electives"])


def _assert_faculty_exists(db: Session, faculty_id: int | None) -> None:
    if faculty_id is not None and not db.query(Faculty).filter(Faculty.id == faculty_id).first():
        raise HTTPException(status_code=400, detail="faculty_id does not refer to an existing faculty member")


def _assert_code_available(db: Session, code: str, department: str, exclude_id: int | None = None) -> None:
    query = db.query(Elective).filter(Elective.code == code, Elective.department == department)
    if exclude_id is not None:
        query = query.filter(Elective.id != exclude_id)
    if query.first():
        raise HTTPException(status_code=400, detail="An elective with this code already exists in this department")


@router.get("", response_model=list[AdminElectiveOut])
def list_electives(
    search: str | None = None,
    department: str | None = None,
    category: str | None = None,
    basket: str | None = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> list[AdminElectiveOut]:
    query = db.query(Elective)
    if department:
        query = query.filter(Elective.department == department)
    if category:
        query = query.filter(Elective.category == category)
    if basket:
        query = query.filter(Elective.basket == basket)
    if search:
        like = f"%{search}%"
        query = query.filter(or_(Elective.code.ilike(like), Elective.title.ilike(like)))
    electives = query.order_by(Elective.code).all()
    return [AdminElectiveOut.model_validate(e) for e in electives]


@router.post("", response_model=AdminElectiveOut, status_code=status.HTTP_201_CREATED)
def create_elective(
    payload: AdminElectiveCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> AdminElectiveOut:
    _assert_faculty_exists(db, payload.faculty_id)
    _assert_code_available(db, payload.code, payload.department)

    elective = Elective(**payload.model_dump())
    db.add(elective)
    db.flush()
    record_audit(db, current_user.id, "create", "elective", elective.id, {"code": elective.code})
    db.commit()
    db.refresh(elective)
    invalidate(ELECTIVES_LIST_CACHE_KEY)
    return AdminElectiveOut.model_validate(elective)


@router.put("/{elective_id}", response_model=AdminElectiveOut)
def update_elective(
    elective_id: int,
    payload: AdminElectiveUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> AdminElectiveOut:
    elective = db.query(Elective).filter(Elective.id == elective_id).first()
    if not elective:
        raise HTTPException(status_code=404, detail="Elective not found")

    updates = payload.model_dump(exclude_unset=True)
    _assert_faculty_exists(db, updates.get("faculty_id"))
    if "code" in updates or "department" in updates:
        new_code = updates.get("code", elective.code)
        new_department = updates.get("department", elective.department)
        _assert_code_available(db, new_code, new_department, exclude_id=elective.id)

    for field, value in updates.items():
        setattr(elective, field, value)
    record_audit(db, current_user.id, "update", "elective", elective.id, {"fields": list(updates.keys())})
    db.commit()
    db.refresh(elective)
    invalidate(ELECTIVES_LIST_CACHE_KEY)
    return AdminElectiveOut.model_validate(elective)


@router.delete("/{elective_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_elective(
    elective_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> None:
    elective = db.query(Elective).filter(Elective.id == elective_id).first()
    if not elective:
        raise HTTPException(status_code=404, detail="Elective not found")
    record_audit(db, current_user.id, "delete", "elective", elective.id, {"code": elective.code})
    db.delete(elective)
    db.commit()
    invalidate(ELECTIVES_LIST_CACHE_KEY)
