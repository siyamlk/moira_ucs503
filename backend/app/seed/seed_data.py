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
from app.models.academic_config import AcademicConfig
from app.models.backlog import Backlog
from app.models.elective import Elective
from app.models.faculty import Faculty
from app.models.faculty_schedule import FacultySchedule
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.recommendation.scoring_engine import SCORE_WEIGHTS
from app.services.academic_config_service import RECOMMENDATION_WEIGHTS_KEY
from app.services.recommendation_service import (
    INTEREST_KEYWORDS,
    derive_elective_career_tags,
    extract_tags,
)

# Dev-only default admin account. Rotate or remove this before any real
# deployment — see docs/ADMIN.md. There is no self-service way to become an
# admin; this seed (or a direct DB update) is the only path.
# NB: must be a real (non-reserved) TLD — email-validator rejects .local/
# .test/.example etc. even though the ORM insert below bypasses that check,
# and the seeded account still needs to log in through the validated
# /api/auth/login endpoint like any other user.
DEFAULT_ADMIN_EMAIL = "admin@moira.app"
DEFAULT_ADMIN_PASSWORD = "AdminPass123!"

# Matches Elective.category's documented value set (see models/elective.py)
# plus the "Professional Elective" fallback used by seed_electives() below.
ELECTIVE_CATEGORIES = [
    "Elective I",
    "Elective II",
    "Elective III",
    "Elective IV",
    "Generic Elective",
    "Professional Elective",
]

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


# Synthetic office-hour slots for the Slot Booking feature to demo against
# locally (see docs/BOOKING.md) — no real timetable data exists yet for most
# departments (README "Current Limitations"), so this is a clearly-labeled
# demo convenience, the same way seed_demo_user() below is a synthetic
# account rather than a real student record, not real faculty availability.
DEMO_SCHEDULE_SLOTS = [
    {"day": "Monday", "start_time": "09:00", "end_time": "10:00", "room": "Room 101"},
    {"day": "Monday", "start_time": "14:00", "end_time": "15:00", "room": "Room 214"},
    {"day": "Tuesday", "start_time": "10:00", "end_time": "11:00", "room": "Room 118"},
    {"day": "Tuesday", "start_time": "15:00", "end_time": "16:00", "room": "Room 305"},
    {"day": "Wednesday", "start_time": "11:00", "end_time": "12:00", "room": "Room 214"},
    {"day": "Thursday", "start_time": "09:00", "end_time": "10:00", "room": "Room 118"},
    {"day": "Thursday", "start_time": "14:00", "end_time": "15:00", "room": "Room 101"},
    {"day": "Friday", "start_time": "11:00", "end_time": "12:00", "room": "Room 305"},
]

# Repeating pattern of how many DEMO_SCHEDULE_SLOTS a given faculty member
# gets, cycling by index so coverage looks varied rather than a uniform
# grid — some professors have one office hour, others several.
DEMO_SCHEDULE_COUNT_CYCLE = [2, 1, 3, 1, 2]


def seed_demo_schedules(db) -> None:
    """Idempotent per faculty member (not a single global guard): skips
    anyone who already has at least one FacultySchedule row — whether from
    a previous run of this function or real admin-entered data — and only
    backfills demo slots for faculty with none, so re-running this (e.g.
    after adding more faculty via a new CSV) never touches existing data,
    demo or real."""
    departments = [source["department"] for source in FACULTY_SOURCES]
    all_faculty = (
        db.query(Faculty)
        .filter(Faculty.department.in_(departments))
        .order_by(Faculty.department, Faculty.name)
        .all()
    )
    already_scheduled = {
        row[0] for row in db.query(FacultySchedule.faculty_id).distinct().all()
    }

    slot_pool_size = len(DEMO_SCHEDULE_SLOTS)
    added_any = False
    for i, faculty in enumerate(all_faculty):
        if faculty.id in already_scheduled:
            continue
        # Leave roughly one in six faculty with no schedule at all, so the
        # directory still shows realistic partial coverage rather than
        # implying every professor's office hours are on file.
        if i % 6 == 5:
            continue
        count = DEMO_SCHEDULE_COUNT_CYCLE[i % len(DEMO_SCHEDULE_COUNT_CYCLE)]
        offset = i % slot_pool_size
        for j in range(count):
            slot = DEMO_SCHEDULE_SLOTS[(offset + j) % slot_pool_size]
            db.add(FacultySchedule(faculty_id=faculty.id, semester="Odd 2026-27", **slot))
        added_any = True
    if added_any:
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


def seed_admin(db) -> None:
    if db.query(User).filter(User.email == DEFAULT_ADMIN_EMAIL).first() is not None:
        return

    admin_user = User(
        full_name="MOIRA Admin",
        student_id="ADMIN-001",
        email=DEFAULT_ADMIN_EMAIL,
        hashed_password=hash_password(DEFAULT_ADMIN_PASSWORD),
        role="admin",
    )
    db.add(admin_user)
    db.flush()

    # Every User needs a profile (see auth.signup) even though an admin
    # never uses the student-facing advisory features themselves.
    db.add(StudentProfile(user_id=admin_user.id))
    db.commit()


def seed_academic_config(db) -> None:
    if db.query(AcademicConfig).count() > 0:
        return
    db.add(
        AcademicConfig(
            key=RECOMMENDATION_WEIGHTS_KEY,
            value=dict(SCORE_WEIGHTS),
            description="Component weights (must sum to 100) used by the elective recommendation engine.",
        )
    )
    db.add(
        AcademicConfig(
            key="elective_categories",
            value=list(ELECTIVE_CATEGORIES),
            description="Valid Elective.category values offered in the admin elective form.",
        )
    )
    db.commit()


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_faculty(db)
        seed_electives(db)
        seed_demo_schedules(db)
        seed_demo_user(db)
        seed_admin(db)
        seed_academic_config(db)
        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
