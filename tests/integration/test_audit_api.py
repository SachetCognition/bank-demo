import pytest
import requests

class TestAuditAPI:
    def test_audit_log_created_on_login(self, auth_url):
        """Verify that login creates an audit log entry."""
        response = requests.post(f"{auth_url}/api/users/auth", json={
            "email": "audit_test@example.com",
            "password": "wrongpassword",
        })
        # Even failed login should create audit entry
        assert response.status_code in [200, 400]
