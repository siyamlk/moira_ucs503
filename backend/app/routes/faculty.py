from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database.connection import get_db
from app.models.faculty import Faculty
from app.schemas.faculty import FacultyOut

router = APIRouter(prefix="/api/faculty", tags=["faculty"])


@router.get("", response_model=list[FacultyOut])
def list_faculty(db: Session = Depends(get_db)) -> list[FacultyOut]:
    faculty = db.query(Faculty).options(joinedload(Faculty.schedules)).all()
    return [FacultyOut.model_validate(f) for f in faculty]


@router.get("/{faculty_id}", response_model=FacultyOut)
def get_faculty(faculty_id: int, db: Session = Depends(get_db)) -> FacultyOut:
    faculty = (
        db.query(Faculty)
        .options(joinedload(Faculty.schedules))
        .filter(Faculty.id == faculty_id)
        .first()
    )
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty member not found")
    return FacultyOut.model_validate(faculty)
