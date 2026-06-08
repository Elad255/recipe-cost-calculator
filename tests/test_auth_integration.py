import pytest


class TestRegister:

    def test_register_success(self, client):
        response = client.post("/auth/register", json={
            "email": "newchef@kitchen.com",
            "password": "pasta123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newchef@kitchen.com"
        assert "id" in data
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client, registered_user):
        response = client.post("/auth/register", json={
            "email": "chef@kitchen.com",
            "password": "different123"
        })
        assert response.status_code == 400

    def test_register_invalid_email(self, client):
        response = client.post("/auth/register", json={
            "email": "not-an-email",
            "password": "test123"
        })
        assert response.status_code == 422


class TestLogin:

    def test_login_success(self, client, registered_user):
        response = client.post("/auth/login", json={
            "email": "chef@kitchen.com",
            "password": "shakshuka123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, registered_user):
        response = client.post("/auth/login", json={
            "email": "chef@kitchen.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post("/auth/login", json={
            "email": "nobody@kitchen.com",
            "password": "test123"
        })
        assert response.status_code == 401


class TestGetMe:

    def test_get_me_authenticated(self, client, auth_headers):
        response = client.get("/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "chef@kitchen.com"

    def test_get_me_no_token(self, client):
        response = client.get("/auth/me")
        assert response.status_code == 401