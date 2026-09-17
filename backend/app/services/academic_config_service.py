"""Reads admin-managed academic configuration for consumption by the
advisory engines. The engines stay responsible for scoring/ranking logic —
this module only supplies the numbers admins are allowed to tune."""

from sqlalchemy.orm import Session

from app.models.academic_config import AcademicConfig
from app.recommendation.scoring_engine import SCORE_WEIGHTS

RECOMMENDATION_WEIGHTS_KEY = "recommendation_weights"


def weights_are_valid(weights: object) -> bool:
    if not isinstance(weights, dict):
        return False
    if set(weights.keys()) != set(SCORE_WEIGHTS.keys()):
        return False
    if not all(isinstance(v, int) and not isinstance(v, bool) for v in weights.values()):
        return False
    return sum(weights.values()) == 100


def get_recommendation_weights(db: Session) -> dict[str, int]:
    """Returns the admin-configured recommendation weights if a valid
    override has been saved, otherwise the hardcoded SCORE_WEIGHTS default.
    Falling back on anything invalid/missing keeps the engine's guaranteed
    "components never sum past 100" property intact even if the config
    table ever ends up in a bad state."""
    row = db.query(AcademicConfig).filter(AcademicConfig.key == RECOMMENDATION_WEIGHTS_KEY).first()
    if row and weights_are_valid(row.value):
        return dict(row.value)
    return dict(SCORE_WEIGHTS)
