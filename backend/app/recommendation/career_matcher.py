"""Connects a student's stated career goal(s) to a specific elective's
actual career-relevance tags. Never asserts a career goal makes a course
"good" in the abstract — only speaks to the concrete overlap that was
computed by the scoring engine.
"""


def career_relevance_text(
    course_title: str, career_goals_raw: list[str], matched_career_tags: list[str]
) -> str:
    if matched_career_tags:
        goal_text = " / ".join(career_goals_raw) if career_goals_raw else " / ".join(matched_career_tags)
        return (
            f"Because you're aiming for {goal_text}, {course_title} has a direct link to that goal — "
            f"its content maps to: {', '.join(matched_career_tags)}."
        )
    if career_goals_raw:
        return (
            f"Your stated goal of {' / '.join(career_goals_raw)} doesn't map directly to a career-focus "
            f"keyword this course's syllabus contains, so career alignment here is weak."
        )
    return "No career goal was provided, so career alignment couldn't be scored for this course."
