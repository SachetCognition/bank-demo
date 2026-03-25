import pytest
import requests
import time

class TestAuthAPI:
    def test_register_user(self, auth_url):
        email = f"test_{int(time.time())}@example.com"
        response = requests.post(f"{auth_url}/api/users", json={
            "name": "Test User",
            "email": email,
            "password": "TestPass123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert data["email"] == email

    def test_register_duplicate_user(self, auth_url):
        email = f"dup_{int(time.time())}@example.com"
        requests.post(f"{auth_url}/api/users", json={
            "name": "Test User",
            "email": email,
            "password": "TestPass123",
        })
        response = requests.post(f"{auth_url}/api/users", json={
            "name": "Test User",
            "email": email,
            "password": "TestPass123",
        })
        assert response.status_code == 400

    def test_login_valid(self, auth_url):
        email = f"login_{int(time.time())}@example.com"
        requests.post(f"{auth_url}/api/users", json={
            "name": "Test User",
            "email": email,
            "password": "TestPass123",
        })
        response = requests.post(f"{auth_url}/api/users/auth", json={
            "email": email,
            "password": "TestPass123",
        })
        assert response.status_code == 200

    def test_login_invalid(self, auth_url):
        response = requests.post(f"{auth_url}/api/users/auth", json={
            "email": "nonexistent@example.com",
            "password": "wrongpass",
        })
        assert response.status_code == 400

    def test_logout(self, auth_url):
        response = requests.post(f"{auth_url}/api/users/logout")
        assert response.status_code == 200
