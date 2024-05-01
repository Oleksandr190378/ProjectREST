
from test_route_contacts import token


def test_get_me(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("api/users/me", headers=headers)
    assert response.status_code == 200, response.text


def test_update_avatar_user(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    test_file_path = "tests/test_data/test_image.jpg"
    with open(test_file_path, "rb") as f:
        files = {"file": ("test_image.jpg", f, "image/jpeg")}
        response = client.patch("/api/users/avatar", files=files, headers=headers)
        assert response.status_code == 200


