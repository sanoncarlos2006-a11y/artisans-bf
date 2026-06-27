from fastapi.testclient import TestClient


def _register_and_login(client: TestClient, *, phone: str, email: str) -> str:
    password = "Password123"
    register_response = client.post(
        "/auth/register",
        json={
            "full_name": "Photo Test User",
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


def _business_payload(name: str = "Atelier Photo Test") -> dict[str, object]:
    return {
        "name": name,
        "category": "Photographe",
        "phone": "70223344",
        "latitude": 12.3714,
        "longitude": -1.5197,
        "address_description": "Secteur de test, Ouagadougou",
        "opening_hours": "Lun-Sam 08:00-18:00",
    }


def _create_business(client: TestClient, token: str) -> int:
    response = client.post(
        "/businesses",
        json=_business_payload(),
        headers=_auth_headers(token),
    )
    assert response.status_code == 201
    return response.json()["id"]


def _tiny_png_bytes(index: int = 0) -> bytes:
    return b"\x89PNG\r\n\x1a\n" + f"test-image-{index}".encode()


def _upload_png(client: TestClient, token: str, business_id: int, index: int = 0):
    return client.post(
        f"/businesses/{business_id}/photos",
        headers=_auth_headers(token),
        files={"file": (f"photo-{index}.png", _tiny_png_bytes(index), "image/png")},
    )


def test_owner_upload_limits_and_public_photo_response(client: TestClient) -> None:
    owner_token = _register_and_login(
        client,
        phone="70200001",
        email="photo.owner@example.test",
    )
    business_id = _create_business(client, owner_token)

    uploaded_photos = []
    for index in range(3):
        response = _upload_png(client, owner_token, business_id, index)
        assert response.status_code == 201
        photo = response.json()
        assert photo["business_id"] == business_id
        assert photo["content_type"] == "image/png"
        assert photo["file_path"].startswith("/uploads/")
        uploaded_photos.append(photo)

    fourth_response = _upload_png(client, owner_token, business_id, 4)
    assert fourth_response.status_code == 400

    text_response = client.post(
        f"/businesses/{business_id}/photos",
        headers=_auth_headers(owner_token),
        files={"file": ("not-image.txt", b"not an image", "text/plain")},
    )
    assert text_response.status_code == 400

    publish_response = client.patch(
        f"/businesses/{business_id}/publish",
        headers=_auth_headers(owner_token),
    )
    assert publish_response.status_code == 200

    public_response = client.get(f"/businesses/{business_id}")
    assert public_response.status_code == 200
    public_photos = public_response.json()["photos"]
    public_photo_ids = {photo["id"] for photo in public_photos}
    assert public_photo_ids == {photo["id"] for photo in uploaded_photos}


def test_other_user_cannot_upload_or_delete_owner_photo(client: TestClient) -> None:
    owner_token = _register_and_login(
        client,
        phone="70200002",
        email="photo.owner.two@example.test",
    )
    other_token = _register_and_login(
        client,
        phone="70200003",
        email="photo.other@example.test",
    )
    business_id = _create_business(client, owner_token)

    upload_response = _upload_png(client, owner_token, business_id)
    assert upload_response.status_code == 201
    photo_id = upload_response.json()["id"]

    other_upload_response = _upload_png(client, other_token, business_id, 1)
    assert other_upload_response.status_code == 404

    other_delete_response = client.delete(
        f"/businesses/{business_id}/photos/{photo_id}",
        headers=_auth_headers(other_token),
    )
    assert other_delete_response.status_code == 404

    owner_photos_response = client.get(
        f"/businesses/{business_id}/photos",
        headers=_auth_headers(owner_token),
    )
    assert owner_photos_response.status_code == 200
    assert [photo["id"] for photo in owner_photos_response.json()] == [photo_id]
