from locust import HttpUser, task, between
from faker import Faker
import time

fake = Faker()

class BankUser(HttpUser):
    wait_time = between(1, 3)
    host = "http://localhost:5000"

    def on_start(self):
        self.email = f"perf_{int(time.time())}_{fake.random_int()}@example.com"
        self.password = "TestPass123"

    @task(3)
    def get_accounts(self):
        self.client.post("/account/allaccounts", data={"email_id": self.email})

    @task(2)
    def get_transaction_history(self):
        self.client.post("/transaction/history", data={"account_number": "IBAN0000000000000000"})

    @task(1)
    def get_loan_history(self):
        self.client.post("/loan/history", data={"email": self.email})

    @task(2)
    def get_accounts_paginated(self):
        self.client.post("/account/allaccounts", data={"email_id": self.email, "page": 1, "page_size": 20})

    @task(1)
    def get_transaction_history_paginated(self):
        self.client.post("/transaction/history", data={"account_number": "IBAN0000000000000000", "page": 1, "page_size": 20})
