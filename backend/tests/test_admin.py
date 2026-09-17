"""Admin subsystem: role-based authorization, CRUD over academic data,
academic configuration, and audit logging. Mirrors the conventions in the
other test_*.py files — auth is always exercised end-to-end through the
real endpoints, never a fabricated JWT."""

from app.models.user import User


def _promote_to_admin(db_session, email: str) -> None:
    user = db_session.query(User).filter(User.email == email).first()
    user.role = "admin"
    db_session.commit()


def _admin_headers(client, db_session, email="admin.user@thapar.edu") -> dict:
    payload = {
        "full_name": "Admin User",
        "student_id": "ADM-001",
        "email": email,
        "password": "AdminPass123",
    }
    response = client.post("/api/auth/signup", json=payload)
    token = response.json()["access_token"]
    _promote_to_admin(db_session, email)
    return {"Authorization": f"Bearer {token}"}


# --- Authorization -----------------------------------------------------


def test_unauthenticated_cannot_access_admin_dashboard(client):
    response = client.get("/api/admin/dashboard")
    assert response.status_code == 401


def test_student_cannot_access_admin_dashboard(client, auth_headers):
    response = client.get("/api/admin/dashboard", headers=auth_headers)
    assert response.status_code == 403


def test_student_cannot_create_elective(client, auth_headers):
    response = client.post(
        "/api/admin/electives",
        json={"code": "UCS999", "title": "Should Not Be Created"},
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_new_signups_default_to_student_role(client, signup_payload):
    response = client.post("/api/auth/signup", json=signup_payload)
    assert response.json()["user"]["role"] == "student"


def test_admin_can_access_dashboard(client, db_session):
    headers = _admin_headers(client, db_session)
    response = client.get("/api/admin/dashboard", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total_electives"] == 0
    assert body["total_faculty"] == 0
    assert body["recent_activity"] == []


# --- Elective CRUD -------------------------------------------------------


def test_admin_elective_crud_lifecycle(client, db_session):
    headers = _admin_headers(client, db_session)

    create = client.post(
        "/api/admin/electives",
        json={
            "code": "UCS900",
            "title": "Applied Machine Learning",
            "department": "Computer Science and Engineering",
            "credits": 4.0,
            "category": "Elective I",
            "interest_tags": ["Machine Learning"],
        },
        headers=headers,
    )
    assert create.status_code == 201
    elective_id = create.json()["id"]
    assert create.json()["title"] == "Applied Machine Learning"

    listed = client.get("/api/admin/electives", headers=headers)
    assert listed.status_code == 200
    assert any(e["id"] == elective_id for e in listed.json())

    searched = client.get("/api/admin/electives?search=Applied", headers=headers)
    assert any(e["id"] == elective_id for e in searched.json())

    updated = client.put(
        f"/api/admin/electives/{elective_id}",
        json={"title": "Applied ML and Deep Learning"},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Applied ML and Deep Learning"
    assert updated.json()["code"] == "UCS900"  # untouched fields survive a partial update

    deleted = client.delete(f"/api/admin/electives/{elective_id}", headers=headers)
    assert deleted.status_code == 204
    assert client.get("/api/admin/electives", headers=headers).json() == []


def test_admin_elective_create_rejects_duplicate_code_in_same_department(client, db_session):
    headers = _admin_headers(client, db_session)
    payload = {"code": "UCS901", "title": "Course A", "department": "Computer Science and Engineering"}
    assert client.post("/api/admin/electives", json=payload, headers=headers).status_code == 201
    dup = client.post("/api/admin/electives", json=payload, headers=headers)
    assert dup.status_code == 400


def test_admin_elective_create_rejects_missing_required_fields(client, db_session):
    headers = _admin_headers(client, db_session)
    response = client.post("/api/admin/electives", json={"title": "No Code"}, headers=headers)
    assert response.status_code == 422


def test_admin_elective_update_rejects_unknown_faculty_id(client, db_session):
    headers = _admin_headers(client, db_session)
    create = client.post(
        "/api/admin/electives", json={"code": "UCS902", "title": "Course B"}, headers=headers
    )
    elective_id = create.json()["id"]
    response = client.put(
        f"/api/admin/electives/{elective_id}", json={"faculty_id": 9999}, headers=headers
    )
    assert response.status_code == 400


def test_admin_elective_delete_missing_returns_404(client, db_session):
    headers = _admin_headers(client, db_session)
    assert client.delete("/api/admin/electives/9999", headers=headers).status_code == 404


# --- Faculty CRUD ----------------------------------------------------------


def test_admin_faculty_crud_lifecycle(client, db_session):
    headers = _admin_headers(client, db_session)

    create = client.post(
        "/api/admin/faculty",
        json={"ref_code": "CSE-900", "name": "Dr. Test Faculty", "department": "Computer Science and Engineering"},
        headers=headers,
    )
    assert create.status_code == 201
    faculty_id = create.json()["id"]

    updated = client.put(
        f"/api/admin/faculty/{faculty_id}", json={"office_location": "Room 214"}, headers=headers
    )
    assert updated.status_code == 200
    assert updated.json()["office_location"] == "Room 214"

    deleted = client.delete(f"/api/admin/faculty/{faculty_id}", headers=headers)
    assert deleted.status_code == 204


def test_admin_faculty_create_rejects_duplicate_ref_code(client, db_session):
    headers = _admin_headers(client, db_session)
    payload = {"ref_code": "CSE-901", "name": "Dr. A"}
    assert client.post("/api/admin/faculty", json=payload, headers=headers).status_code == 201
    dup = client.post("/api/admin/faculty", json={**payload, "name": "Dr. B"}, headers=headers)
    assert dup.status_code == 400


def test_admin_cannot_delete_faculty_with_assigned_electives(client, db_session):
    headers = _admin_headers(client, db_session)
    faculty = client.post(
        "/api/admin/faculty", json={"ref_code": "CSE-902", "name": "Dr. Assigned"}, headers=headers
    ).json()
    client.post(
        "/api/admin/electives",
        json={"code": "UCS903", "title": "Course C", "faculty_id": faculty["id"]},
        headers=headers,
    )

    response = client.delete(f"/api/admin/faculty/{faculty['id']}", headers=headers)
    assert response.status_code == 409

    # Clearing the assignment first should unblock the delete.
    electives = client.get("/api/admin/electives", headers=headers).json()
    elective_id = next(e["id"] for e in electives if e["code"] == "UCS903")
    client.put(f"/api/admin/electives/{elective_id}", json={"faculty_id": None}, headers=headers)
    assert client.delete(f"/api/admin/faculty/{faculty['id']}", headers=headers).status_code == 204


# --- Schedule CRUD -----------------------------------------------------


def test_admin_schedule_crud_lifecycle(client, db_session):
    headers = _admin_headers(client, db_session)
    faculty = client.post(
        "/api/admin/faculty", json={"ref_code": "CSE-903", "name": "Dr. Schedule"}, headers=headers
    ).json()

    create = client.post(
        "/api/admin/schedules",
        json={
            "faculty_id": faculty["id"],
            "day": "Monday",
            "start_time": "10:00",
            "end_time": "11:00",
            "semester": "Odd 2026-27",
        },
        headers=headers,
    )
    assert create.status_code == 201
    schedule_id = create.json()["id"]
    assert create.json()["semester"] == "Odd 2026-27"

    listed = client.get(f"/api/admin/schedules?faculty_id={faculty['id']}", headers=headers)
    assert len(listed.json()) == 1

    updated = client.put(f"/api/admin/schedules/{schedule_id}", json={"room": "LT-1"}, headers=headers)
    assert updated.status_code == 200
    assert updated.json()["room"] == "LT-1"

    assert client.delete(f"/api/admin/schedules/{schedule_id}", headers=headers).status_code == 204


def test_admin_schedule_create_rejects_unknown_faculty(client, db_session):
    headers = _admin_headers(client, db_session)
    response = client.post(
        "/api/admin/schedules",
        json={"faculty_id": 9999, "day": "Monday", "start_time": "10:00", "end_time": "11:00"},
        headers=headers,
    )
    assert response.status_code == 400


def test_deleting_faculty_cascades_its_schedules(client, db_session):
    headers = _admin_headers(client, db_session)
    faculty = client.post(
        "/api/admin/faculty", json={"ref_code": "CSE-904", "name": "Dr. Cascade"}, headers=headers
    ).json()
    client.post(
        "/api/admin/schedules",
        json={"faculty_id": faculty["id"], "day": "Tuesday", "start_time": "09:00", "end_time": "10:00"},
        headers=headers,
    )
    client.delete(f"/api/admin/faculty/{faculty['id']}", headers=headers)
    remaining = client.get(f"/api/admin/schedules?faculty_id={faculty['id']}", headers=headers)
    assert remaining.json() == []


# --- Academic config / recommendation weights --------------------------


def test_admin_can_read_and_update_recommendation_weights(client, db_session):
    headers = _admin_headers(client, db_session)
    new_weights = {
        "interest": 30,
        "career": 20,
        "syllabus": 20,
        "skill": 15,
        "academic": 10,
        "prerequisite": 5,
    }
    response = client.put(
        "/api/admin/config/recommendation_weights",
        json={"value": new_weights, "description": "Retuned for pilot cohort"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["value"] == new_weights

    fetched = client.get("/api/admin/config/recommendation_weights", headers=headers)
    assert fetched.json()["value"] == new_weights


def test_recommendation_weights_update_rejects_invalid_sum(client, db_session):
    headers = _admin_headers(client, db_session)
    bad_weights = {
        "interest": 50,
        "career": 50,
        "syllabus": 20,
        "skill": 15,
        "academic": 10,
        "prerequisite": 5,
    }
    response = client.put(
        "/api/admin/config/recommendation_weights",
        json={"value": bad_weights},
        headers=headers,
    )
    assert response.status_code == 400


def test_updated_recommendation_weights_are_used_by_the_engine(client, db_session):
    headers = _admin_headers(client, db_session)
    # Push all weight onto "interest" so a course matching only interests
    # should score 100, proving the engine actually reads the admin config
    # rather than the hardcoded default.
    all_weight_on_interest = {
        "interest": 100,
        "career": 0,
        "syllabus": 0,
        "skill": 0,
        "academic": 0,
        "prerequisite": 0,
    }
    client.put(
        "/api/admin/config/recommendation_weights",
        json={"value": all_weight_on_interest},
        headers=headers,
    )
    client.post(
        "/api/admin/electives",
        json={
            "code": "UCS904",
            "title": "Course D",
            "interest_tags": ["Machine Learning"],
            "topics": ["Machine Learning"],
        },
        headers=headers,
    )

    response = client.post(
        "/api/recommendations",
        json={"student_profile": {"interests": ["Machine Learning"]}},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["weights"] == all_weight_on_interest


def test_generic_config_key_can_be_created_and_read(client, db_session):
    headers = _admin_headers(client, db_session)
    response = client.put(
        "/api/admin/config/elective_categories",
        json={"value": ["Elective I", "Elective II"], "description": "Trimmed for pilot"},
        headers=headers,
    )
    assert response.status_code == 200
    all_config = client.get("/api/admin/config", headers=headers).json()
    assert any(c["key"] == "elective_categories" for c in all_config)


# --- Audit log -----------------------------------------------------------


def test_admin_actions_are_recorded_in_audit_log(client, db_session):
    headers = _admin_headers(client, db_session)
    create = client.post(
        "/api/admin/electives", json={"code": "UCS905", "title": "Course E"}, headers=headers
    )
    elective_id = create.json()["id"]

    log = client.get("/api/admin/audit-log", headers=headers)
    assert log.status_code == 200
    entries = log.json()
    assert any(
        e["action"] == "create" and e["entity_type"] == "elective" and e["entity_id"] == elective_id
        for e in entries
    )


def test_student_cannot_read_audit_log(client, auth_headers):
    response = client.get("/api/admin/audit-log", headers=auth_headers)
    assert response.status_code == 403
