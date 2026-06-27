from fastapi.testclient import TestClient


def _register_and_login(client: TestClient, *, phone: str, email: str) -> str:
    password = "Password123"
    register_response = client.post(
        "/auth/register",
        json={
            "full_name": "Business Test User",
            "phone": phone,
            "email": email,
            "password": password,
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={"identifier": phone, "password": password},
    )
    assert login_response.status_code == 200
    return login_response.json()["access_token"]


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _business_payload(name: str = "Atelier Test") -> dict[str, object]:
    return {
        "name": name,
        "category": "Couturier",
        "phone": "70112233",
        "latitude": 12.3714,
        "longitude": -1.5197,
        "address_description": "Rue de test, Ouagadougou",
        "opening_hours": "Lun-Sam 08:00-18:00",
    }


def _public_business_ids(client: TestClient) -> set[int]:
    response = client.get("/businesses")
    assert response.status_code == 200
    return {business["id"] for business in response.json()}


def test_business_public_visibility_and_owner_protection(client: TestClient) -> None:
    owner_token = _register_and_login(
        client,
        phone="70100001",
        email="business.owner@example.test",
    )

    create_response = client.post(
        "/businesses",
        json=_business_payload(),
        headers=_auth_headers(owner_token),
    )
    assert create_response.status_code == 201
    created_business = create_response.json()
    business_id = created_business["id"]
    assert created_business["status"] == "draft"

    assert business_id not in _public_business_ids(client)

    publish_response = client.patch(
        f"/businesses/{business_id}/publish",
        headers=_auth_headers(owner_token),
    )
    assert publish_response.status_code == 200
    assert publish_response.json()["status"] == "published"
    assert business_id in _public_business_ids(client)

    unpublish_response = client.patch(
        f"/businesses/{business_id}/unpublish",
        headers=_auth_headers(owner_token),
    )
    assert unpublish_response.status_code == 200
    assert unpublish_response.json()["status"] == "unpublished"
    assert business_id not in _public_business_ids(client)

    owner_list_response = client.get("/my-businesses", headers=_auth_headers(owner_token))
    assert owner_list_response.status_code == 200
    owner_businesses = owner_list_response.json()
    assert any(business["id"] == business_id for business in owner_businesses)

    other_token = _register_and_login(
        client,
        phone="70100002",
        email="business.other@example.test",
    )
    other_headers = _auth_headers(other_token)

    update_response = client.put(
        f"/businesses/{business_id}",
        json={"name": "Tentative Modification"},
        headers=other_headers,
    )
    assert update_response.status_code == 404

    publish_by_other_response = client.patch(
        f"/businesses/{business_id}/publish",
        headers=other_headers,
    )
    assert publish_by_other_response.status_code == 404

    delete_by_other_response = client.delete(
        f"/businesses/{business_id}",
        headers=other_headers,
    )
    assert delete_by_other_response.status_code == 404

    owner_detail_response = client.get(
        f"/businesses/{business_id}/owner",
        headers=_auth_headers(owner_token),
    )
    assert owner_detail_response.status_code == 200
    owner_detail = owner_detail_response.json()
    assert owner_detail["name"] == created_business["name"]
    assert owner_detail["status"] == "unpublished"
