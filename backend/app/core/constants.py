"""Canonical branch/department names, shared by the seed data, the elective
recommendation filter, and the frontend's branch picker (see
frontend/src/utils/branches.ts, which mirrors this list).

These must match Elective.department values exactly for branch-aware
filtering to work (see routes/electives.py).
"""

BRANCH_DEPARTMENTS: list[str] = [
    "Computer Science and Engineering",
    "Computer Engineering",
    "Electronics and Communication Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Electronics and Computer Engineering",
]

# Open/Generic electives are available to students of any branch.
OPEN_ELECTIVE_DEPARTMENT = "Open Elective (All Branches)"
