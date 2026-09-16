def test_signup_creates_user_and_returns_token(client, signup_payload):
    response = client.post("/api/auth/signup", json=signup_payload)
    assert response.status_code == 201
    body = response.json()
    assert body["access_token"]
    assert body["user"]["email"] == signup_payload["email"]


def test_signup_rejects_duplicate_email(client, signup_payload):
    client.post("/api/auth/signup", json=signup_payload)
    response = client.post("/api/auth/signup", json=signup_payload)
    assert response.status_code == 400


def test_login_with_correct_credentials(client, signup_payload):
    client.post("/api/auth/signup", json=signup_payload)
    response = client.post(
        "/api/auth/login",
        json={"email": signup_payload["email"], "password": signup_payload["password"]},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_with_wrong_password_fails(client, signup_payload):
    client.post("/api/auth/signup", json=signup_payload)
    response = client.post(
        "/api/auth/login", json={"email": signup_payload["email"], "password": "WrongPass1"}
    )
    assert response.status_code == 401


def test_me_requires_valid_token(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["full_name"] == "Test Student"


def test_me_rejects_missing_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401
