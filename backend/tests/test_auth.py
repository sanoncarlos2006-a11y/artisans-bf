from fastapi.testclient import TestClient


def _registration_payload(
    *,
    phone: str = "70000001",
    email: str = "auth.user@example.test",
    password: str = "Password123",
) -> dict[str, str]:
    return {
        "full_name": "Auth Test User",
        "phone": phone,
        "email": email,
        "password": password,
    }


def _assert_no_password_hash(value: object) -> None:
    if isinstance(value, dict):
        assert "password_hash" not in value
        for child in value.values():
            _assert_no_password_hash(child)
    elif isinstance(value, list):
        for child in value:
            _assert_no_password_hash(child)


def test_health_check_works(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_login_and_me_flow(client: TestClient) -> None:
    payload = _registration_payload()

    register_response = client.post("/auth/register", json=payload)
    assert register_response.status_code == 201
    registered_user = register_response.json()
    assert registered_user["phone"] == payload["phone"]
    _assert_no_password_hash(registered_user)

    login_response = client.post(
        "/auth/login",
        json={"identifier": payload["phone"], "password": payload["password"]},
    )
    assert login_response.status_code == 200
    login_body = login_response.json()
    assert login_body["access_token"]
    assert login_body["token_type"] == "bearer"
    _assert_no_password_hash(login_body)

    me_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {login_body['access_token']}"},
    )
    assert me_response.status_code == 200
    me_body = me_response.json()
    assert me_body["phone"] == payload["phone"]
    _assert_no_password_hash(me_body)


def test_login_with_wrong_password_fails(client: TestClient) -> None:
    payload = _registration_payload(phone="70000002", email="wrong.password@example.test")
    assert client.post("/auth/register", json=payload).status_code == 201

    response = client.post(
        "/auth/login",
        json={"identifier": payload["phone"], "password": "WrongPassword123"},
    )

    assert response.status_code == 401


def test_duplicate_phone_registration_fails(client: TestClient) -> None:
    payload = _registration_payload(phone="70000003", email="first@example.test")
    assert client.post("/auth/register", json=payload).status_code == 201

    duplicate_response = client.post(
        "/auth/register",
        json=_registration_payload(phone=payload["phone"], email="second@example.test"),
    )

    assert duplicate_response.status_code == 409
