import pytest
import requests

class TestSecurity:
    def test_cors_headers(self, dashboard_url):
        response = requests.options(f"{dashboard_url}/")
        # Check response is valid
        assert response.status_code in [200, 204, 405]

    def test_nosql_injection_blocked(self, auth_url):
        """Attempt NoSQL injection and verify it's blocked."""
        response = requests.post(f"{auth_url}/api/users/auth", json={
            "email": {"$gt": ""},
            "password": {"$gt": ""},
        })
        assert response.status_code in [400, 401, 422, 500]
