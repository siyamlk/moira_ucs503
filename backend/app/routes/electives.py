from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.constants import OPEN_ELECTIVE_DEPARTMENT
from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.elective import Elective
from app.models.faculty import Faculty
from app.models.user import User
from app.schemas.elective import (
    ElectiveOut,
    RecommendationOut,
    RecommendRequest,
    RecommendResponse,
    ScoreBreakdown,
)
from app.schemas.faculty import FacultyOut
from app.services.recommendation_service import (
    build_explanation,
    normalize_career_goal,
    normalize_interests,
    score_elective,
    suggest_faculty,
)

router = APIRouter(prefix="/api/electives", tags=["electives"])


@router.get("", response_model=list[ElectiveOut])
def list_electives(
    department: str | None = None, db: Session = Depends(get_db)
) -> list[ElectiveOut]:
    query = db.query(Elective).options(joinedload(Elective.faculty))
    if department:
        query = query.filter(Elective.department == department)
    electives = query.all()
    return [ElectiveOut.model_validate(e) for e in electives]


@router.get("/{elective_id}", response_model=ElectiveOut)
def get_elective(elective_id: int, db: Session = Depends(get_db)) -> ElectiveOut:
    elective = (
        db.query(Elective)
        .options(joinedload(Elective.faculty))
        .filter(Elective.id == elective_id)
        .first()
    )
    if not elective:
        raise HTTPException(status_code=404, detail="Elective not found")
    return ElectiveOut.model_validate(elective)


@router.post("/recommend", response_model=RecommendResponse)
def recommend_electives(
    payload: RecommendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecommendResponse:
    interest_tags = normalize_interests(payload.free_text, payload.interests)
    career_tags = normalize_career_goal(payload.free_text, payload.career_goal)

    profile = current_user.profile
    profile.interests = interest_tags
    profile.career_goal = payload.career_goal or profile.career_goal
    profile.raw_intent_text = payload.free_text
    db.commit()

    electives_query = db.query(Elective).options(joinedload(Elective.faculty))
    if profile.branch:
        # Only this student's own branch, plus open/generic electives that any
        # branch can take. Students who haven't set a branch yet see everything,
        # rather than being shown zero recommendations before onboarding.
        electives_query = electives_query.filter(
            Elective.department.in_([profile.branch, OPEN_ELECTIVE_DEPARTMENT])
        )
    electives = electives_query.all()
    all_faculty = db.query(Faculty).options(joinedload(Faculty.schedules)).all()

    scored: list[RecommendationOut] = []
    for elective in electives:
        score, matched_topics, interest_match, career_match, breakdown = score_elective(
            interest_tags,
            career_tags,
            elective.interest_tags,
            elective.career_tags,
            elective.topics,
        )
        explanation = build_explanation(
            elective.title,
            interest_tags,
            profile.career_goal,
            matched_topics,
            interest_match,
            career_match,
            breakdown,
        )
        matched_faculty = suggest_faculty(
            all_faculty, interest_tags or matched_topics, elective.department
        )
        scored.append(
            RecommendationOut(
                elective=ElectiveOut.model_validate(elective),
                match_percent=score,
                interest_match=interest_match,
                career_match=career_match,
                matched_topics=matched_topics,
                explanation=explanation,
                score_breakdown=ScoreBreakdown(**breakdown),
                suggested_faculty=[FacultyOut.model_validate(f) for f in matched_faculty],
            )
        )

    scored.sort(key=lambda r: r.match_percent, reverse=True)

    return RecommendResponse(
        interpreted_tags=interest_tags,
        career_goal=profile.career_goal,
        top_recommendation=scored[0] if scored else None,
        alternatives=scored[1:6],
    )
