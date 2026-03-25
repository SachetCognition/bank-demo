import pytest
import requests
import time

class TestAccountsAPI:
    def test_create_account(self, dashboard_url):
        response = requests.post(f"{dashboard_url}/account/create", data={
            "email_id": f"test_{int(time.time())}@example.com",
            "account_type": "Checking",
            "address": "123 Test St",
            "govt_id_number": "123456789",
            "government_id_type": "SSN",
            "name": "Test User",
        })
        assert response.status_code == 200

    def test_get_all_accounts(self, dashboard_url):
        response = requests.post(f"{dashboard_url}/account/allaccounts", data={
            "email_id": "test@example.com",
        })
        assert response.status_code == 200

    def test_get_account_details(self, dashboard_url):
        response = requests.post(f"{dashboard_url}/account/detail", data={
            "account_number": "IBAN0000000000000000",
        })
        assert response.status_code == 200
