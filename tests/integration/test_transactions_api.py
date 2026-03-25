import pytest
import requests
import time

class TestTransactionsAPI:
    def test_transaction_history(self, dashboard_url):
        response = requests.post(f"{dashboard_url}/transaction/history", data={
            "account_number": "IBAN0000000000000000",
        })
        assert response.status_code == 200

    def test_send_money(self, dashboard_url):
        response = requests.post(f"{dashboard_url}/transaction/", data={
            "sender_account_number": "IBAN0000000000000001",
            "receiver_account_number": "IBAN0000000000000002",
            "amount": "10",
            "sender_account_type": "Checking",
            "receiver_account_type": "Checking",
            "reason": "Test transfer",
        })
        assert response.status_code == 200
