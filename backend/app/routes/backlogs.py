from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.backlog import Backlog
from app.models.user import User
from app.schemas.backlog import (
    BacklogCreate,
    BacklogOut,
    PrioritizedBacklogOut,
    PrioritizeResponse,
)
from app.services.backlog_service import prioritize

router = APIRouter(prefix="/api/backlogs", tags=["backlogs"])


@router.get("", response_model=list[BacklogOut])
def list_backlogs(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[BacklogOut]:
    backlogs = db.query(Backlog).filter(Backlog.user_id == current_user.id).all()
    return [BacklogOut.model_validate(b) for b in backlogs]


@router.post("", response_model=BacklogOut, status_code=201)
def create_backlog(
    payload: BacklogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BacklogOut:
    backlog = Backlog(user_id=current_user.id, **payload.model_dump())
    db.add(backlog)
    db.commit()
    db.refresh(backlog)
    return BacklogOut.model_validate(backlog)


@router.delete("/{backlog_id}", status_code=204)
def delete_backlog(
    backlog_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    backlog = (
        db.query(Backlog)
        .filter(Backlog.id == backlog_id, Backlog.user_id == current_user.id)
        .first()
    )
    if not backlog:
        raise HTTPException(status_code=404, detail="Backlog not found")
    db.delete(backlog)
    db.commit()


@router.post("/prioritize", response_model=PrioritizeResponse)
def prioritize_backlogs(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> PrioritizeResponse:
    backlogs = (
        db.query(Backlog)
        .filter(Backlog.user_id == current_user.id, Backlog.status == "pending")
        .all()
    )
    profile = current_user.profile
    results = prioritize(backlogs, profile.cgpa, profile.credits_earned)

    prioritized = [
        PrioritizedBacklogOut(
            backlog=BacklogOut.model_validate(r["backlog"]),
            priority_rank=r["priority_rank"],
            priority_label=r["priority_label"],
            cgpa_impact=r["cgpa_impact"],
            estimated_new_cgpa=r["estimated_new_cgpa"],
            explanation=r["explanation"],
        )
        for r in results
    ]

    return PrioritizeResponse(
        current_cgpa=profile.cgpa, pending_count=len(backlogs), prioritized=prioritized
    )
