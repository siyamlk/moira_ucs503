"""Seed the database with real course-scheme and faculty data where available,
falling back to a demo student account for local testing.

Sources (see backend/app/seed/data/):
- faculty_cse.csv / faculty_ece.csv: Thapar CSED/ECED faculty directories
  (name, designation, specialization, email, and — for ECE — office room).
  Mechanical, Civil and ENC to follow once that data is provided.
- electives_cse.csv / electives_coe.csv: Professional Elective (PEC) baskets
  transcribed from the official 2025 B.E. CSE / COE course scheme documents
  (Elective I-IV), including real course codes and credits.
- electives_open.csv: Generic/Open Electives (OEC), available to students of
  any branch — see OPEN_ELECTIVE_DEPARTMENT in core/constants.py.
- electives_efb_details.csv: per-course description, prerequisites (where
  explicitly stated) and syllabus_outline (real unit/module headers),
  transcribed from the official Elective Focus Basket (EFB) syllabus
  document approved at the 2nd Academic Council meeting (8 Dec 2025). Only
  merged into CSE/COE electives (ENRICHED_DEPARTMENTS below) — the doc
  doesn't cover every branch's basket, and the user asked for this
  enrichment scoped to COE and CSE specifically.

Interest/career tags on each elective are mechanically derived via the same
keyword vocabulary the recommendation engine uses (see
recommendation_service.py). For CSE/COE electives with an EFB details row,
tags are derived from title + description (richer, more accurate matches);
everything else falls back to title-only derivation, since no richer
syllabus-level data was available for it at seed time.

Elective.department values must exactly match the canonical branch names in
core/constants.BRANCH_DEPARTMENTS so that branch-aware filtering in
routes/electives.py (a student only sees their own branch's electives, plus
open electives) actually matches. StudentProfile.branch must be set to one
of those same canonical strings — the frontend branch picker
(frontend/src/utils/branches.ts) enforces this by offering only that list.

Run with: python -m app.seed.seed_data
"""

import csv
from pathlib import Path

from app.core.security import hash_password
from app.database.base import Base
from app.database.connection import SessionLocal, engine
from app.models.backlog import Backlog
from app.models.elective import Elective
from app.models.faculty import Faculty
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.services.recommendation_service import (
    INTEREST_KEYWORDS,
    derive_elective_career_tags,
    extract_tags,
)

DATA_DIR = Path(__file__).parent / "data"

FACULTY_SOURCES = [
    {
        "file": "faculty_cse.csv",
        "department": "Computer Science and Engineering",
        "prefix": "CSE",
        "columns": {"name": "name", "title": "designation", "specialization": "specialization", "email": "email"},
    },
    {
        "file": "faculty_ece.csv",
        "department": "Electronics and Communication Engineering",
        "prefix": "ECE",
        "columns": {
            "name": "Teacher Name",
            "title": "Designation",
            "specialization": "Area of Specialization",
            "email": "Email",
            "office_location": "Room No.",
            "ref_code": "Faulty Code",
        },
    },
]

ELECTIVE_SOURCES = ["electives_cse.csv", "electives_coe.csv", "electives_open.csv"]
ELECTIVE_DETAILS_FILE = "electives_efb_details.csv"
# Only these departments have EFB syllabus-sourced descriptions/outlines
# available (see module docstring) — the user asked for this enrichment
# scoped to COE and CSE.
ENRICHED_DEPARTMENTS = {"Computer Science and Engineering", "Computer Engineering"}

# Curriculum rule: a student commits to ONE Elective Focus Basket (EFB) and
# takes Elective I, II, III and IV from *within that same basket only* —
# they are not offered as a free-for-all mix-and-match across baskets. This
# maps each course code to its basket, exactly as grouped under each "EFB
# ___" section heading in the official EFB syllabus document. Courses not
# listed here (e.g. the connected-vehicles electives, which the source
# document doesn't group under a named "EFB ___" heading) are left with an
# empty basket — i.e. not subject to the basket-lock rule, since no basket
# name for them is confirmed in the source.
CODE_TO_BASKET: dict[str, str] = {
    # EFB High Performance Computing
    "UCS531": "High Performance Computing",
    "UCS635": "High Performance Computing",
    "UCS645": "High Performance Computing",
    "UCS751": "High Performance Computing",
    # EFB Computer Animation and Gaming
    "UCS636": "Computer Animation and Gaming",
    "UCS646": "Computer Animation and Gaming",
    "UCS752": "Computer Animation and Gaming",
    # EFB Information and Cyber Security
    "UCS534": "Information and Cyber Security",
    "UCS638": "Information and Cyber Security",
    "UCS648": "Information and Cyber Security",
    "UCS754": "Information and Cyber Security",
    # EFB Mathematics and Computing
    "UMC512": "Mathematics and Computing",
    "UMC622": "Mathematics and Computing",
    "UMC632": "Mathematics and Computing",
    "UMC742": "Mathematics and Computing",
    # EFB Data Science
    "UCS548": "Data Science",
    "UCS654": "Data Science",
    "UCS772": "Data Science",
    "UCS761": "Data Science",
    # EFB Financial Derivative
    "UCS539": "Financial Derivative",
    "UCS675": "Financial Derivative",
    "UCS658": "Financial Derivative",
    "UMC743": "Financial Derivative",
    # EFB DevOps and Continuous Delivery
    "UCS537": "DevOps and Continuous Delivery",
    "UCS659": "DevOps and Continuous Delivery",
    "UCS660": "DevOps and Continuous Delivery",
    "UCS758": "DevOps and Continuous Delivery",
    # EFB Full Stack
    "UCS542": "Full Stack",
    "UCS662": "Full Stack",
    "UCS745": "Full Stack",
    # EFB Conversational AI
    "UCS551": "Conversational AI",
    "UCS664": "Conversational AI",
    "UCS749": "Conversational AI",
    "UCS748": "Conversational AI",
    # EFB Robotics and Edge AI
    "UCS547": "Robotics and Edge AI",
    "UCS671": "Robotics and Edge AI",
    "UCS760": "Robotics and Edge AI",
    # EFB Cyber Forensics and Ethical Hacking
    "UCS550": "Cyber Forensics and Ethical Hacking",
    "UCS673": "Cyber Forensics and Ethical Hacking",
    "UCS674": "Cyber Forensics and Ethical Hacking",
    "UCS750": "Cyber Forensics and Ethical Hacking",
}

DEMO_BACKLOGS = [
    {"subject": "Data Structures", "course_code": "UCS301", "credits": 4.0, "course_type": "Professional Core Course", "current_grade": "F"},
    {"subject": "Operating System", "course_code": "UCS303", "credits": 4.0, "course_type": "Professional Core Course", "current_grade": "F"},
    {"subject": "Discrete Mathematical Structures", "course_code": "UCS405", "credits": 3.5, "course_type": "Professional Core Course", "current_grade": "E"},
]


def seed_faculty(db) -> None:
    if db.query(Faculty).count() > 0:
        return
    for source in FACULTY_SOURCES:
        path = DATA_DIR / source["file"]
        if not path.exists():
            continue
        columns = source["columns"]
        with open(path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):

                def col(key: str) -> str:
                    src_col = columns.get(key)
                    return (row.get(src_col) or "").strip() if src_col else ""

                specialization = col("specialization")
                research_interests = [s.strip() for s in specialization.split(",") if s.strip()]
                raw_ref = col("ref_code")
                ref_code = f"{source['prefix']}-{raw_ref}" if raw_ref else f"{source['prefix']}-{i:03d}"
                db.add(
                    Faculty(
                        ref_code=ref_code,
                        name=col("name"),
                        title=col("title"),
                        department=source["department"],
                        specialization=specialization,
                        research_interests=research_interests,
                        office_location=col("office_location"),
                        email=col("email"),
                        photo_url=col("photo_url"),
                        profile_url=col("profile_url"),
                    )
                )
    db.commit()


def _load_elective_details() -> dict[str, dict[str, object]]:
    """Load per-code EFB syllabus enrichment: description, prerequisites
    (where explicit) and syllabus_outline (real unit headers, "|"-joined)."""
    path = DATA_DIR / ELECTIVE_DETAILS_FILE
    details: dict[str, dict[str, object]] = {}
    if not path.exists():
        return details
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row["code"].strip()
            outline_raw = (row.get("syllabus_outline") or "").strip()
            details[code] = {
                "description": (row.get("description") or "").strip()[:1000],
                "prerequisites": (row.get("prerequisites") or "").strip()[:200],
                "syllabus_outline": [t.strip() for t in outline_raw.split("|") if t.strip()],
            }
    return details


def seed_electives(db) -> None:
    if db.query(Elective).count() > 0:
        return
    details_by_code = _load_elective_details()
    seen_codes: set[tuple[str, str]] = set()
    for filename in ELECTIVE_SOURCES:
        path = DATA_DIR / filename
        if not path.exists():
            continue
        with open(path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = row["code"].strip()
                department = row["department"].strip()
                key = (code, department)
                if key in seen_codes:
                    continue
                seen_codes.add(key)

                title = row["title"].strip()

                details = details_by_code.get(code) if department in ENRICHED_DEPARTMENTS else None
                description = str(details["description"]) if details else ""
                prerequisites = str(details["prerequisites"]) if details else ""
                syllabus_outline = list(details["syllabus_outline"]) if details else []

                # With a syllabus description available, derive tags from
                # title + description instead of title alone — far more
                # accurate matches (a title like "UI & UX Specialist" won't
                # itself say "user interface", but its description does).
                tag_source = f"{title} {description}" if details else title
                interest_tags = extract_tags(tag_source, INTEREST_KEYWORDS)
                career_tags = derive_elective_career_tags(tag_source, interest_tags)

                db.add(
                    Elective(
                        code=code,
                        title=title,
                        department=department,
                        credits=float(row["credits"]),
                        # NB: the CSV's own "basket" column actually holds the
                        # Elective I-IV slot label; that maps to `category`.
                        # The *EFB* basket (e.g. "Data Science") is a
                        # separate concept — see CODE_TO_BASKET above.
                        category=row.get("basket", "").strip() or "Professional Elective",
                        basket=CODE_TO_BASKET.get(code, ""),
                        prerequisites=prerequisites,
                        description=description,
                        topics=interest_tags,
                        syllabus_outline=syllabus_outline,
                        interest_tags=interest_tags,
                        career_tags=career_tags,
                        faculty_id=None,  # no fixed instructor in the source scheme data
                    )
                )
    db.commit()


def seed_demo_user(db) -> None:
    if db.query(User).filter(User.email == "alex.chen@thapar.edu").first() is not None:
        return

    demo_user = User(
        full_name="Alex Chen",
        student_id="21BCD-041",
        email="alex.chen@thapar.edu",
        hashed_password=hash_password("Demo@1234"),
    )
    db.add(demo_user)
    db.flush()

    profile = StudentProfile(
        user_id=demo_user.id,
        semester=5,
        branch="Computer Science and Engineering",  # must match Elective.department exactly
        cgpa=7.2,
        credits_earned=60,
        credits_required=165,  # from BECSE25.pdf total credit scheme
        career_goal="AI/ML Engineer",
        interests=["Artificial Intelligence", "Machine Learning", "Data Science"],
        raw_intent_text=(
            "I enjoy AI, data analysis, and programming, and I want to work in "
            "healthcare predictive systems and autonomous systems."
        ),
    )
    db.add(profile)

    for backlog in DEMO_BACKLOGS:
        db.add(Backlog(user_id=demo_user.id, **backlog))

    db.commit()


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_faculty(db)
        seed_electives(db)
        seed_demo_user(db)
        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
