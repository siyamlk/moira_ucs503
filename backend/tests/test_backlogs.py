from app.models.backlog import Backlog
from app.services.backlog_service import estimate_cgpa_impact, grade_point, prioritize


def test_grade_point_maps_known_grades():
    assert grade_point("F") == 0.0
    assert grade_point("a") == 10.0
    assert grade_point("unknown") == 0.0


def test_estimate_cgpa_impact_higher_credits_move_cgpa_more():
    # current_cgpa (7.0) is above the assumed clear grade point (6.0), so clearing a
    # backlog nudges the CGPA down slightly toward 6.0 — larger credits produce a
    # bigger swing, i.e. a larger-magnitude (more negative) impact.
    _, small_impact = estimate_cgpa_impact(current_cgpa=7.0, credits_earned=60, backlog_credits=2.0)
    _, large_impact = estimate_cgpa_impact(current_cgpa=7.0, credits_earned=60, backlog_credits=6.0)
    assert abs(large_impact) > abs(small_impact)


def test_estimate_cgpa_impact_moves_toward_assumed_grade_point():
    new_cgpa, impact = estimate_cgpa_impact(current_cgpa=5.0, credits_earned=40, backlog_credits=4.0)
    assert new_cgpa > 5.0
    assert impact > 0


def test_prioritize_ranks_highest_impact_first():
    backlogs = [
        Backlog(id=1, subject="Discrete Mathematics", course_code="MA102", credits=3.0, current_grade="E"),
        Backlog(id=2, subject="Data Structures", course_code="CS201", credits=4.0, current_grade="F"),
        Backlog(id=3, subject="Operating Systems", course_code="CS304", credits=4.0, current_grade="F"),
    ]
    results = prioritize(backlogs, current_cgpa=7.0, credits_earned=60)

    assert results[0]["priority_rank"] == 1
    assert results[0]["priority_label"] == "CRITICAL"
    assert results[1]["priority_label"] == "HIGH"
    assert results[2]["priority_label"] == "MODERATE"
    # Higher-credit backlogs move CGPA more (in magnitude) and should rank above the
    # 3-credit one, regardless of the sign of the swing.
    assert results[0]["backlog"].credits == 4.0
    magnitudes = [abs(r["cgpa_impact"]) for r in results]
    assert magnitudes == sorted(magnitudes, reverse=True)


def test_create_and_prioritize_backlogs_via_api(client, auth_headers):
    payload = {
        "subject": "Data Structures",
        "course_code": "CS201",
        "credits": 4.0,
        "course_type": "Prerequisite Course",
        "current_grade": "F",
    }
    create_response = client.post("/api/backlogs", json=payload, headers=auth_headers)
    assert create_response.status_code == 201

    list_response = client.get("/api/backlogs", headers=auth_headers)
    assert len(list_response.json()) == 1

    prioritize_response = client.post("/api/backlogs/prioritize", headers=auth_headers)
    assert prioritize_response.status_code == 200
    body = prioritize_response.json()
    assert body["pending_count"] == 1
    assert body["prioritized"][0]["priority_label"] == "CRITICAL"
    assert body["prioritized"][0]["backlog"]["course_code"] == "CS201"


def test_prioritize_requires_auth(client):
    response = client.post("/api/backlogs/prioritize")
    assert response.status_code == 401


def test_prioritize_falls_back_to_credit_weight_when_no_credits_earned():
    # Regression test: with credits_earned == 0 the weighted-average formula
    # has no baseline to blend into, so every backlog used to collapse to the
    # same estimated_new_cgpa (== ASSUMED_CLEAR_GRADE_POINT) regardless of its
    # credits — i.e. different-credit subjects showed an identical cgpa_impact.
    backlogs = [
        Backlog(id=1, subject="Discrete Mathematics", course_code="MA102", credits=3.0, current_grade="F"),
        Backlog(id=2, subject="Data Structures", course_code="CS201", credits=4.0, current_grade="F"),
    ]
    results = prioritize(backlogs, current_cgpa=7.0, credits_earned=0)

    assert all(r["cgpa_impact"] == 0.0 for r in results)
    # No usable CGPA signal, so it must still differentiate — by credit weight.
    assert results[0]["backlog"].credits == 4.0
    assert results[1]["backlog"].credits == 3.0
    assert "credits earned" in results[0]["explanation"].lower()
