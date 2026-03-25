import pytest
import requests

class TestLoansAPI:
    def test_loan_history(self, dashboard_url):
        response = requests.post(f"{dashboard_url}/loan/history", data={
            "email": "test@example.com",
        })
        assert response.status_code == 200

    def test_loan_request(self, dashboard_url):
        response = requests.post(f"{dashboard_url}/loan/", data={
            "name": "Test User",
            "email": "test@example.com",
            "account_type": "Checking",
            "account_number": "IBAN0000000000000000",
            "govt_id_type": "SSN",
            "govt_id_number": "123456789",
            "loan_type": "Personal",
            "loan_amount": "1000",
            "interest_rate": "5.0",
            "time_period": "12",
        })
        assert response.status_code == 200
