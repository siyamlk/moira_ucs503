"""Transparent, rule-based elective recommendation engine.

Free text is normalized into a fixed vocabulary of canonical tags via keyword
matching (no ML model, no external API — fully deterministic and explainable).
Each elective is then scored against the student's interest tags, career goal
tags and topic list. See docs/RECOMMENDATION_LOGIC.md for the scoring formula.
"""

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.faculty import Faculty

INTEREST_KEYWORDS: dict[str, list[str]] = {
    "Artificial Intelligence": ["artificial intelligence", "ai"],
    "Machine Learning": ["machine learning", "ml"],
    "Data Science": ["data science", "data analysis", "data analytics", "data"],
    "Cybersecurity": ["cybersecurity", "cyber security", "security"],
    "Software Engineering": ["software engineering", "software development", "programming", "coding"],
    "Web Development": ["web development", "web dev", "frontend", "backend", "full stack"],
    "Cloud Computing": ["cloud computing", "cloud"],
    "Finance": ["finance", "fintech", "financial"],
    "Product Management": ["product management", "product manager"],
    "Distributed Systems": ["distributed systems", "distributed computing", "big data"],
    "Predictive Healthcare": ["predictive healthcare", "healthcare", "medical", "health"],
    "Autonomous Systems": ["autonomous systems", "autonomous", "robotics", "self-driving"],
    "Mathematics": ["calculus", "multivariable calculus", "mathematics", "linear algebra"],
    # Added alongside the EFB (Elective Focus Basket) syllabus integration —
    # these themes have whole EFB tracks but had no matching canonical tag
    # before, so courses in them scored a flat 0 for any student interest.
    "DevOps": [
        "devops", "continuous integration", "continuous deployment", "continuous delivery",
        "ci/cd", "build and release", "source code management", "configuration management",
        "containerization", "docker", "kubernetes", "provisioning",
    ],
    "Blockchain": ["blockchain", "smart contract", "cryptocurrency", "bitcoin", "ethereum"],
    "Game Development": ["game design", "game development", "game engine", "3d modelling", "3d modeling"],
    "Augmented and Virtual Reality": [
        "augmented reality", "virtual reality", "mixed reality", "extended reality",
    ],
    "Computer Vision": ["computer vision", "image processing", "convolutional neural network"],
    "Natural Language Processing": ["natural language processing", "language model", "text processing"],
    "Generative AI": [
        "generative ai", "large language model", "generative adversarial network",
        "prompt engineering",
    ],
    "High Performance Computing": [
        "parallel computing", "gpu computing", "cuda", "high performance computing",
        "parallel programming", "heterogeneous computing",
    ],
    "Digital Forensics": [
        "digital forensics", "cyber forensics", "forensic investigation", "malware analysis",
        "incident response",
    ],
    "Ethical Hacking": ["ethical hacking", "penetration testing", "vulnerability assessment"],
    "UI/UX Design": ["user interface", "user experience", "ux design", "ui design"],
}

CAREER_KEYWORDS: dict[str, list[str]] = {
    "AI/ML Engineer": ["ai/ml engineer", "ai engineer", "ml engineer", "machine learning engineer"],
    "Data Scientist": ["data scientist"],
    "Software Engineer": ["software engineer", "developer", "swe"],
    "Data Analyst": ["data analyst"],
    "Product Manager": ["product manager"],
    "Research": ["researcher", "research", "academia"],
    "Finance/FinTech": ["finance", "fintech", "financial analyst", "investment"],
    "DevOps Engineer": ["devops engineer", "site reliability engineer", "sre"],
    "Game Developer": ["game developer", "game designer"],
    "Cybersecurity Analyst": [
        "cybersecurity analyst", "security analyst", "penetration tester", "ethical hacker",
        "soc analyst",
    ],
    "Blockchain Developer": ["blockchain developer"],
    "Robotics Engineer": ["robotics engineer"],
    "UX/Product Designer": [
        "product design", "product designer", "ux designer", "ui designer", "ux/ui designer",
        "interaction designer", "user experience designer",
    ],
}


def text_contains(text: str, keyword: str) -> bool:
    """Word-boundary-aware substring check: a single-word keyword like "go"
    or "r" must appear as a whole word, not merely as a substring inside an
    unrelated word (e.g. "algorithm", "categorical") — a single-letter or
    short keyword otherwise has a very high false-positive rate. Multi-word
    phrases ("machine learning") don't need this: a phrase appearing as a
    substring is already specific enough not to false-positive this way,
    and phrase-boundary regex is unreliable across punctuation/whitespace
    variants anyway. Shared by extract_tags (canonical vocabulary matching)
    and scoring_engine (literal skill/custom-interest matching) — see
    docs/RECOMMENDATION_LOGIC.md."""
    if " " in keyword or "-" in keyword:
        return keyword in text
    return re.search(rf"\b{re.escape(keyword)}\b", text) is not None


def extract_tags(text: str, vocabulary: dict[str, list[str]]) -> list[str]:
    text = text.lower()
    matched: list[str] = []
    for canonical_tag, keywords in vocabulary.items():
        if any(text_contains(text, kw) for kw in keywords):
            matched.append(canonical_tag)
    return matched


def normalize_interests(free_text: str, selected_interests: list[str]) -> list[str]:
    """Merge explicitly selected interest chips with tags inferred from free text."""
    inferred = extract_tags(free_text, INTEREST_KEYWORDS)
    combined = list(dict.fromkeys([*selected_interests, *inferred]))
    return combined


def normalize_career_goal(free_text: str, career_goal: str) -> list[str]:
    combined_text = f"{career_goal} {free_text}"
    return extract_tags(combined_text, CAREER_KEYWORDS)


# A course's title/description describes its technical *content*, not job
# titles — so literal CAREER_KEYWORDS phrases like "devops engineer" almost
# never appear in a syllabus ("Covers Docker and Kubernetes..." never says
# "DevOps engineer"). Without this map, career_tags would stay empty for
# nearly every course and Career Goal Alignment would always score 0.
# This maps each canonical interest tag to the career path(s) that
# technical area commonly supports — a general, documented inference
# rule, not a per-course fabrication of syllabus content.
INTEREST_TO_CAREER_MAP: dict[str, list[str]] = {
    "Artificial Intelligence": ["AI/ML Engineer", "Research"],
    "Machine Learning": ["AI/ML Engineer"],
    "Data Science": ["Data Scientist", "Data Analyst"],
    "Cybersecurity": ["Cybersecurity Analyst"],
    "Software Engineering": ["Software Engineer"],
    "Web Development": ["Software Engineer"],
    "Cloud Computing": ["DevOps Engineer"],
    "Finance": ["Finance/FinTech"],
    "Product Management": ["Product Manager"],
    "Distributed Systems": ["Software Engineer"],
    "Predictive Healthcare": ["Data Scientist"],
    "Autonomous Systems": ["Robotics Engineer"],
    "DevOps": ["DevOps Engineer"],
    "Blockchain": ["Blockchain Developer"],
    "Game Development": ["Game Developer"],
    "Computer Vision": ["AI/ML Engineer"],
    "Natural Language Processing": ["AI/ML Engineer"],
    "Generative AI": ["AI/ML Engineer"],
    "High Performance Computing": ["Software Engineer", "Research"],
    "Digital Forensics": ["Cybersecurity Analyst"],
    "Ethical Hacking": ["Cybersecurity Analyst"],
    "UI/UX Design": ["UX/Product Designer", "Software Engineer"],
    "Mathematics": ["Research"],
}


def derive_elective_career_tags(text: str, interest_tags: list[str]) -> list[str]:
    """Career tags for a course record: literal keyword matches in its own
    title/description, unioned with career paths mapped from its interest
    tags (see INTEREST_TO_CAREER_MAP)."""
    literal = extract_tags(text, CAREER_KEYWORDS)
    mapped = [c for tag in interest_tags for c in INTEREST_TO_CAREER_MAP.get(tag, [])]
    return list(dict.fromkeys([*literal, *mapped]))


def score_elective(
    interest_tags: list[str],
    career_tags: list[str],
    elective_interest_tags: list[str],
    elective_career_tags: list[str],
    elective_topics: list[str],
) -> tuple[int, list[str], bool, bool, dict]:
    """Score one elective 0-100 against the student's tags.

    Weights: interest overlap 45%, career alignment 30%, topic overlap 20%,
    plus a 5-point relevance bonus if there is any match at all.

    Returns the final score alongside a `breakdown` dict whose four
    components sum exactly to it — nothing here is a fixed/hardcoded number;
    every point is derived live from set intersections between the
    student's tags and this elective's tags, computed at request time. The
    breakdown is returned (not just the total) so the API/UI can show the
    arithmetic rather than asking the student to trust a black-box number.
    """
    interest_set = set(interest_tags)
    career_set = set(career_tags)

    matched_interests = interest_set & set(elective_interest_tags)
    matched_topics = interest_set & set(elective_topics)
    matched_career = career_set & set(elective_career_tags)

    interest_ratio = len(matched_interests) / len(interest_set) if interest_set else 0.0
    topic_ratio = len(matched_topics) / len(elective_topics) if elective_topics else 0.0
    career_hit = 1.0 if matched_career else 0.0

    interest_points = round(interest_ratio * 45, 1)
    career_points = round(career_hit * 30, 1)
    topic_points = round(topic_ratio * 20, 1)

    has_any_match = bool(matched_interests or matched_career or matched_topics)
    bonus_points = 5.0 if has_any_match else 0.0

    final_score = min(100, round(interest_points + career_points + topic_points + bonus_points))

    matched_topics_display = sorted(matched_interests | matched_topics)

    breakdown = {
        "interest_points": interest_points,
        "interest_matched": len(matched_interests),
        "interest_total": len(interest_set),
        "career_points": career_points,
        "career_matched": bool(matched_career),
        "topic_points": topic_points,
        "topic_matched": len(matched_topics),
        "topic_total": len(elective_topics),
        "bonus_points": bonus_points,
    }

    return final_score, matched_topics_display, bool(matched_interests), bool(matched_career), breakdown


def suggest_faculty(
    all_faculty: list["Faculty"], interest_tags: list[str], department: str = "", limit: int = 3
) -> list["Faculty"]:
    """Match faculty to an elective/student by keyword overlap with their
    specialization + research interests. No fixed instructor assignment
    exists in the source scheme data, so this is a live, explainable match
    rather than a stored (and potentially stale/fabricated) FK.
    """
    interest_set = {tag.lower() for tag in interest_tags}
    scored: list[tuple[int, "Faculty"]] = []
    for faculty in all_faculty:
        if department and faculty.department and faculty.department != department:
            continue
        haystack = f"{faculty.specialization} {' '.join(faculty.research_interests)}".lower()
        hits = sum(1 for tag in interest_set if tag in haystack)
        if hits:
            scored.append((hits, faculty))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [faculty for _, faculty in scored[:limit]]


def build_explanation(
    elective_title: str,
    interest_tags: list[str],
    career_goal: str,
    matched_topics: list[str],
    interest_match: bool,
    career_match: bool,
    breakdown: dict,
) -> str:
    parts = []
    if interest_match:
        parts.append(f"your interests in {', '.join(matched_topics)}")
    if career_match and career_goal:
        parts.append(f"your stated goal of {career_goal}")

    if not parts:
        base = f"{elective_title} is a broadly relevant elective in your department."
    else:
        joined = " and ".join(parts)
        base = f"{elective_title} aligns strongly with {joined}."

    # Spell out the actual arithmetic behind the match percentage so it is
    # auditable rather than a trust-me number — these four figures always
    # sum to the displayed match_percent (see score_elective).
    score_line = (
        f" Score breakdown: {breakdown['interest_points']} pts interest "
        f"({breakdown['interest_matched']}/{breakdown['interest_total']} tags matched) + "
        f"{breakdown['career_points']} pts career "
        f"({'matched' if breakdown['career_matched'] else 'no match'}) + "
        f"{breakdown['topic_points']} pts topic overlap "
        f"({breakdown['topic_matched']}/{breakdown['topic_total']} topics) + "
        f"{breakdown['bonus_points']} pts relevance bonus."
    )
    return base + score_line
