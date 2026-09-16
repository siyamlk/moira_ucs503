"""Turns the scoring engine's computed factors into human-readable
explanation text. Every sentence here is built strictly from data passed
in by the caller (matched tags, matched syllabus lines, matched skills,
completed courses, prerequisite checks) — nothing is invented to make an
explanation "sound better."
"""

from app.recommendation.career_matcher import career_relevance_text
from app.recommendation.scoring_engine import PrerequisiteCheck, ScoredMatch
from app.recommendation.syllabus_matcher import syllabus_alignment_text


def _prerequisite_context(prerequisite_checks: list[PrerequisiteCheck], has_prereq_text: bool) -> str:
    if not has_prereq_text:
        return "No explicit prerequisites are listed for this course."
    satisfied = [c.name for c in prerequisite_checks if c.satisfied]
    missing = [c.name for c in prerequisite_checks if not c.satisfied]
    parts = []
    if satisfied:
        parts.append(f"Prerequisites already met: {', '.join(satisfied)}.")
    if missing:
        parts.append(f"Not yet on your completed-courses list: {', '.join(missing)}.")
    return " ".join(parts) if parts else "No explicit prerequisites are listed for this course."


def _academic_context(
    elective_category: str,
    elective_slot: str | None,
    slot_matched: bool | None,
    elective_basket: str,
    current_basket: str,
    completed_courses: list[str],
) -> str:
    text = f"This course is offered under the {elective_category} slot."
    if elective_slot is not None:
        text += (
            " That matches the elective slot you're choosing from this term."
            if slot_matched
            else f" You said you're choosing from {elective_slot}, so this falls outside that slot."
        )
    if elective_basket:
        text += f" It belongs to the {elective_basket} EFB basket — Elective I-IV all come from this same basket."
        if current_basket:
            text += (
                " That matches the basket you've already committed to."
                if current_basket == elective_basket
                else f" You've already committed to {current_basket}, so this course isn't actually available to you."
            )
        else:
            text += " Picking it will lock in this basket for your Elective I-IV choices."
    if completed_courses:
        preview = ", ".join(completed_courses[:5])
        text += f" Courses you've already completed on file: {preview}."
    return text


def _skill_alignment_text(matched_skills: list[str]) -> str:
    if matched_skills:
        return f"Skills you listed that this course's syllabus text actually mentions: {', '.join(matched_skills)}."
    return "None of the skills you listed were found in this course's title, description or syllabus text."


def _why_this_matches(
    course_title: str,
    matched_interests: list[str],
    matched_career_tags: list[str],
    matched_topics: list[str],
) -> str:
    parts = []
    if matched_interests:
        parts.append(f"your stated interest(s) in {', '.join(matched_interests)}")
    if matched_career_tags:
        parts.append(f"your career goal's focus on {', '.join(matched_career_tags)}")
    if not parts and matched_topics:
        parts.append(f"syllabus topics ({', '.join(matched_topics)}) related to what you're exploring")
    if not parts:
        return f"{course_title} didn't match any of your stated interests, career goal or syllabus topics directly."
    return f"{course_title} matches {' and '.join(parts)}."


def build_recommendation_texts(
    *,
    course_title: str,
    scored: ScoredMatch,
    career_goals_raw: list[str],
    completed_courses: list[str],
    elective_slot: str | None,
    elective_category: str,
    elective_basket: str,
    current_basket: str,
    elective_description: str,
    elective_syllabus_outline: list[str],
    elective_prerequisites: str,
) -> dict[str, str | list[str]]:
    # Reuse the exact lines the scoring engine already matched (see
    # scoring_engine.score_elective) rather than recomputing independently
    # — guarantees the score and its explanation can never disagree about
    # which syllabus content actually caused the match.
    matched_syllabus_lines = scored.matched_syllabus_lines

    why_this_matches = _why_this_matches(
        course_title, scored.matched_interests, scored.matched_career_tags, scored.matched_topics
    )
    career_relevance = career_relevance_text(course_title, career_goals_raw, scored.matched_career_tags)
    syllabus_alignment = syllabus_alignment_text(course_title, matched_syllabus_lines, elective_description)
    skill_alignment = _skill_alignment_text(scored.matched_skills)
    academic_context = _academic_context(
        elective_category, elective_slot, scored.slot_matched, elective_basket, current_basket, completed_courses
    )
    prerequisite_context = _prerequisite_context(
        scored.prerequisite_checks, has_prereq_text=bool(elective_prerequisites.strip())
    )

    explanation = f"{why_this_matches} {syllabus_alignment} {career_relevance}"

    return {
        "why_this_matches": why_this_matches,
        "career_relevance": career_relevance,
        "syllabus_alignment": syllabus_alignment,
        "skill_alignment": skill_alignment,
        "academic_context": academic_context,
        "prerequisite_context": prerequisite_context,
        "explanation": explanation,
        "matched_syllabus_lines": matched_syllabus_lines,
    }
