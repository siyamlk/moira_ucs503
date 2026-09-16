"""Identifies which parts of the *actual* EFB syllabus caused a course to
match a student's profile.

Every string this module returns is either a literal syllabus_outline
entry (a real unit/module header transcribed from the EFB catalogue — see
backend/app/seed/data/electives_efb_details.csv) or the course's own
sourced description. Nothing here is inferred from the course title and
nothing is invented — if a course has no syllabus_outline on file, this
module says so rather than guessing.
"""

from app.services.recommendation_service import CAREER_KEYWORDS, INTEREST_KEYWORDS, text_contains


def _keyword_pool(tags: list[str], skills: list[str]) -> set[str]:
    pool: set[str] = set()
    for tag in tags:
        pool.update(k.lower() for k in INTEREST_KEYWORDS.get(tag, []))
        pool.update(k.lower() for k in CAREER_KEYWORDS.get(tag, []))
    pool.update(s.strip().lower() for s in skills if s.strip())
    return pool


def find_matched_syllabus_lines(
    matched_tags: list[str], skills: list[str], syllabus_outline: list[str]
) -> list[str]:
    """Real syllabus_outline lines whose text actually contains a keyword
    tied to one of the student's matched interest/career tags or a skill
    they listed. Returns [] rather than fabricating a line if nothing
    genuinely matches.

    Uses text_contains (word-boundary-aware) rather than a plain substring
    check: several canonical keywords are short single words ("ai", "ml",
    "r") that would otherwise false-positive inside unrelated words in a
    syllabus line (e.g. "ai" inside "maintain", "against", "explain") —
    citing that as "evidence" the course covers AI would be a fabricated
    match, exactly what this module's docstring promises not to do."""
    if not syllabus_outline:
        return []
    keyword_pool = _keyword_pool(matched_tags, skills)
    if not keyword_pool:
        return []
    return [
        line for line in syllabus_outline if any(text_contains(line.lower(), kw) for kw in keyword_pool)
    ]


def syllabus_alignment_text(course_title: str, matched_lines: list[str], description: str) -> str:
    if matched_lines:
        return f"The {course_title} syllabus explicitly covers: {'; '.join(matched_lines)}."
    if description:
        return f"Sourced course description on file: {description}"
    return (
        f"No detailed unit-wise syllabus is on file for {course_title} yet — "
        "matching is based only on its title and department."
    )
