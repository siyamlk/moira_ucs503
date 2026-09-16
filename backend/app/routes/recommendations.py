from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.recommendation.recommendation_service import generate_recommendations
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.post("", response_model=RecommendationResponse)
def recommend(
    payload: RecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecommendationResponse:
    # Did the caller actually include a `student_profile` object, or was it
    # omitted (defaulted) entirely? MOIRA's own UI always includes it (with
    # whatever's currently selected, even if that's an empty list) — only a
    # bare `{}` request (no other caller does this today) omits it, meaning
    # "nothing new, reuse my stored profile". See profile_analyzer.analyze_profile
    # for why this distinction matters (an empty list from real form state
    # must NOT be treated the same as "not provided").
    student_profile_provided = "student_profile" in payload.model_fields_set
    return generate_recommendations(db, current_user, payload, student_profile_provided)
