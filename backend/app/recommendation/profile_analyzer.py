"""Turns a recommendation request + the student's stored profile into a
single normalized AnalyzedProfile the rest of the recommendation package
scores against.

Reuses the existing canonical tag vocabulary (INTEREST_KEYWORDS /
CAREER_KEYWORDS) from app.services.recommendation_service rather than
inventing a second one — "interests" and "preferred domains" both resolve
through the same keyword map, since a domain like "Cybersecurity" or
"Cloud/DevOps" already has a canonical interest tag.
"""

from dataclasses import dataclass, field

from app.services.recommendation_service import (
    CAREER_KEYWORDS,
    INTEREST_KEYWORDS,
    extract_tags,
)


@dataclass
class AnalyzedProfile:
    branch: str
    semester: int
    interest_tags: list[str] = field(default_factory=list)
    career_tags: list[str] = field(default_factory=list)
    # Interest/domain text the student typed that does NOT match any
    # canonical tag in INTEREST_KEYWORDS (e.g. "Sustainable Computing").
    # Previously this was silently dropped entirely — canonical_interests
    # below filters it out, and it's the only thing carrying it — so a
    # custom interest with no known synonym had literally zero effect on
    # scoring even though the UI showed it as an accepted chip. Now it's
    # passed through to scoring_engine and matched literally against course
    # title/description/syllabus text, the same mechanism `skills` already
    # uses (see recommendation_service._build_item).
    custom_interest_terms: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    completed_courses: list[str] = field(default_factory=list)
    career_preference: str = ""
    current_basket: str = ""


def _merge(explicit: list[str], stored: list[str]) -> list[str]:
    """Explicit request values take precedence; fall back to what's on the
    stored profile so the student never has to repeat themselves on a
    second call — de-duplicated, order preserved."""
    combined = explicit if explicit else stored
    return list(dict.fromkeys(v for v in combined if v))


def analyze_profile(request_profile, stored_profile, student_profile_provided: bool = True) -> AnalyzedProfile:
    """
    request_profile: schemas.recommendation.StudentProfileIn (this call's input)
    stored_profile: models.student_profile.StudentProfile (the DB record)
    student_profile_provided: whether the caller actually included a
        `student_profile` object in the request (see routes/recommendations.py,
        which checks payload.model_fields_set). This distinguishes two very
        different situations that an *empty* list on request_profile can't
        tell apart on its own:

          - The caller omitted `student_profile` entirely (e.g. a bare `{}`
            request) — genuinely "nothing new to say", so reuse the stored
            profile as-is. This is the "student never has to repeat
            themselves" convenience _merge() exists for.
          - The caller DID send a `student_profile` (as MOIRA's own UI
            always does — see RecommendationsPage.tsx), but with a field
            left empty because the student cleared/never checked that chip.
            Falling back to the stored value here would be wrong: it makes
            a deliberately-cleared selection impossible to submit, since an
            explicit empty list is indistinguishable from "didn't ask" once
            it reaches _merge(). This silently resurrected stale interests/
            career goals from an earlier session/test on every later call
            (and _persist_profile_updates then re-saved them, so they never
            went away) — see docs/RECOMMENDATION_LOGIC.md.

    When student_profile_provided is True, request_profile's own lists are
    used as-is (no stored-profile fallback); only when False do we fall
    back to `stored_profile` for these fields.
    """
    free_text = request_profile.free_text or ""

    if student_profile_provided:
        interests_raw = list(dict.fromkeys(v for v in request_profile.interests if v))
        domains_raw = list(dict.fromkeys(v for v in request_profile.preferred_domains if v))
        career_goals_raw = list(dict.fromkeys(v for v in request_profile.career_goals if v))
    else:
        interests_raw = _merge(request_profile.interests, stored_profile.interests)
        domains_raw = _merge(request_profile.preferred_domains, stored_profile.preferred_domains)
        career_goals_raw = _merge(
            request_profile.career_goals, [stored_profile.career_goal] if stored_profile.career_goal else []
        )

    # Interest tags: explicit interest chips + preferred-domain chips (a
    # "domain" like Cybersecurity is functionally an interest for matching
    # purposes) + anything inferable from free text.
    interest_text = f"{' '.join(interests_raw)} {' '.join(domains_raw)} {free_text}"
    interest_tags = list(
        dict.fromkeys([*interests_raw, *domains_raw, *extract_tags(interest_text, INTEREST_KEYWORDS)])
    )
    # Keep only tags that are actually canonical for scoring against
    # elective.interest_tags (a controlled vocabulary — see Elective model).
    canonical_interests = [t for t in interest_tags if t in INTEREST_KEYWORDS]
    # What's left over — raw text the student explicitly typed as an
    # interest/domain that never resolved to a canonical tag — isn't
    # thrown away; see custom_interest_terms' docstring above.
    custom_interest_terms = [
        t for t in list(dict.fromkeys([*interests_raw, *domains_raw])) if t not in INTEREST_KEYWORDS
    ]

    career_text = f"{' '.join(career_goals_raw)} {free_text}"
    career_tags = extract_tags(career_text, CAREER_KEYWORDS)
    # A career goal chip that's already a canonical tag counts directly too.
    career_tags = list(dict.fromkeys([*[g for g in career_goals_raw if g in CAREER_KEYWORDS], *career_tags]))

    if student_profile_provided:
        skills = list(dict.fromkeys(v for v in request_profile.skills if v))
        completed_courses = list(dict.fromkeys(v for v in request_profile.completed_courses if v))
        career_preference = request_profile.career_preference
        current_basket = request_profile.current_basket
    else:
        skills = _merge(request_profile.skills, stored_profile.skills)
        completed_courses = _merge(request_profile.completed_courses, stored_profile.completed_courses)
        career_preference = request_profile.career_preference or stored_profile.career_preference
        current_basket = request_profile.current_basket or stored_profile.current_basket

    return AnalyzedProfile(
        branch=stored_profile.branch,
        semester=request_profile.semester or stored_profile.semester,
        interest_tags=canonical_interests,
        custom_interest_terms=custom_interest_terms,
        career_tags=career_tags,
        skills=skills,
        completed_courses=completed_courses,
        career_preference=career_preference,
        current_basket=current_basket,
    )


_SLOT_ALIASES: dict[str, str] = {
    "electivei": "Elective I",
    "elective1": "Elective I",
    "electiveii": "Elective II",
    "elective2": "Elective II",
    "electiveiii": "Elective III",
    "elective3": "Elective III",
    "electiveiv": "Elective IV",
    "elective4": "Elective IV",
    "genericelective": "Generic Elective",
    "openelective": "Generic Elective",
}


def normalize_elective_slot(raw: str | None) -> str | None:
    if not raw or not raw.strip():
        return None
    key = raw.strip().lower().replace(" ", "").replace("-", "").replace("_", "")
    return _SLOT_ALIASES.get(key, raw.strip())
