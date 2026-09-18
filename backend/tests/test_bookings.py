"""Slot booking: a student reserving one of a faculty member's real,
admin-entered schedule slots. Mirrors test_admin.py's conventions — auth is
always exercised end-to-end through the real endpoints."""

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


def _student_headers(client, email="second.student@thapar.edu") -> dict:
    payload = {
        "full_name": "Second Student",
        "student_id": "TS-002",
        "email": email,
        "password": "SecurePass123",
    }
    response = client.post("/api/auth/signup", json=payload)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _create_schedule(client, admin_headers) -> int:
    faculty = client.post(
        "/api/admin/faculty",
        json={"ref_code": "CSE-950", "name": "Dr. Booking Test"},
        headers=admin_headers,
    ).json()
    schedule = client.post(
        "/api/admin/schedules",
        json={
            "faculty_id": faculty["id"],
            "day": "Monday",
            "start_time": "10:00",
            "end_time": "11:00",
            "semester": "Odd 2026-27",
        },
        headers=admin_headers,
    ).json()
    return schedule["id"]


def test_student_can_book_an_open_slot(client, db_session, auth_headers):
    admin_headers = _admin_headers(client, db_session)
    schedule_id = _create_schedule(client, admin_headers)

    response = client.post(
        "/api/bookings", json={"faculty_schedule_id": schedule_id}, headers=auth_headers
    )
    assert response.status_code == 201
    body = response.json()
    assert body["faculty_schedule_id"] == schedule_id
    assert body["status"] == "booked"
    assert body["schedule"]["is_booked"] is True


def test_booking_requires_auth(client, db_session):
    admin_headers = _admin_headers(client, db_session)
    schedule_id = _create_schedule(client, admin_headers)
    response = client.post("/api/bookings", json={"faculty_schedule_id": schedule_id})
    assert response.status_code == 401


def test_booking_unknown_slot_returns_404(client, auth_headers):
    response = client.post(
        "/api/bookings", json={"faculty_schedule_id": 9999}, headers=auth_headers
    )
    assert response.status_code == 404


def test_cannot_double_book_same_slot(client, db_session, auth_headers):
    admin_headers = _admin_headers(client, db_session)
    schedule_id = _create_schedule(client, admin_headers)
    other_headers = _student_headers(client)

    first = client.post(
        "/api/bookings", json={"faculty_schedule_id": schedule_id}, headers=auth_headers
    )
    assert first.status_code == 201

    second = client.post(
        "/api/bookings", json={"faculty_schedule_id": schedule_id}, headers=other_headers
    )
    assert second.status_code == 409


def test_cancelling_a_booking_frees_the_slot_for_another_student(client, db_session, auth_headers):
    admin_headers = _admin_headers(client, db_session)
    schedule_id = _create_schedule(client, admin_headers)
    other_headers = _student_headers(client)

    booking = client.post(
        "/api/bookings", json={"faculty_schedule_id": schedule_id}, headers=auth_headers
    ).json()

    cancel = client.delete(f"/api/bookings/{booking['id']}", headers=auth_headers)
    assert cancel.status_code == 204

    assert client.get("/api/bookings", headers=auth_headers).json() == []

    rebooked = client.post(
        "/api/bookings", json={"faculty_schedule_id": schedule_id}, headers=other_headers
    )
    assert rebooked.status_code == 201


def test_cannot_cancel_another_students_booking(client, db_session, auth_headers):
    admin_headers = _admin_headers(client, db_session)
    schedule_id = _create_schedule(client, admin_headers)
    other_headers = _student_headers(client)

    booking = client.post(
        "/api/bookings", json={"faculty_schedule_id": schedule_id}, headers=auth_headers
    ).json()

    response = client.delete(f"/api/bookings/{booking['id']}", headers=other_headers)
    assert response.status_code == 404


def test_faculty_listing_reflects_booked_status(client, db_session, auth_headers):
    admin_headers = _admin_headers(client, db_session)
    schedule_id = _create_schedule(client, admin_headers)

    before = client.get("/api/faculty").json()
    schedule_before = next(
        s for f in before for s in f["schedules"] if s["id"] == schedule_id
    )
    assert schedule_before["is_booked"] is False

    client.post("/api/bookings", json={"faculty_schedule_id": schedule_id}, headers=auth_headers)

    after = client.get("/api/faculty").json()
    schedule_after = next(
        s for f in after for s in f["schedules"] if s["id"] == schedule_id
    )
    assert schedule_after["is_booked"] is True


# --- Admin visibility ----------------------------------------------------


def test_admin_can_see_a_students_booking(client, db_session, auth_headers):
    admin_headers = _admin_headers(client, db_session)
    schedule_id = _create_schedule(client, admin_headers)
    client.post("/api/bookings", json={"faculty_schedule_id": schedule_id}, headers=auth_headers)

    response = client.get("/api/admin/bookings", headers=admin_headers)
    assert response.status_code == 200
    bookings = response.json()
    assert len(bookings) == 1
    assert bookings[0]["status"] == "booked"
    assert bookings[0]["student_name"] == "Test Student"
    assert bookings[0]["schedule"]["id"] == schedule_id


def test_student_cannot_access_admin_bookings(client, auth_headers):
    response = client.get("/api/admin/bookings", headers=auth_headers)
    assert response.status_code == 403


def test_unauthenticated_cannot_access_admin_bookings(client):
    response = client.get("/api/admin/bookings")
    assert response.status_code == 401


def test_admin_can_force_cancel_a_booking(client, db_session, auth_headers):
    admin_headers = _admin_headers(client, db_session)
    schedule_id = _create_schedule(client, admin_headers)
    booking = client.post(
        "/api/bookings", json={"faculty_schedule_id": schedule_id}, headers=auth_headers
    ).json()

    response = client.delete(f"/api/admin/bookings/{booking['id']}", headers=admin_headers)
    assert response.status_code == 204

    # The student's own active-bookings list should no longer show it...
    assert client.get("/api/bookings", headers=auth_headers).json() == []
    # ...and the slot is open for someone else to book again.
    other_headers = _student_headers(client)
    rebooked = client.post(
        "/api/bookings", json={"faculty_schedule_id": schedule_id}, headers=other_headers
    )
    assert rebooked.status_code == 201


def test_admin_bookings_filterable_by_faculty(client, db_session, auth_headers):
    admin_headers = _admin_headers(client, db_session)
    schedule_id = _create_schedule(client, admin_headers)
    client.post("/api/bookings", json={"faculty_schedule_id": schedule_id}, headers=auth_headers)

    schedule = client.get("/api/admin/schedules", headers=admin_headers).json()
    matching_faculty_id = next(s["faculty_id"] for s in schedule if s["id"] == schedule_id)

    response = client.get(f"/api/admin/bookings?faculty_id={matching_faculty_id}", headers=admin_headers)
    assert len(response.json()) == 1

    response_other = client.get("/api/admin/bookings?faculty_id=999999", headers=admin_headers)
    assert response_other.json() == []
