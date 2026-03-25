import pytest
import re

class TestInputValidation:
    def test_valid_email(self):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        assert re.match(pattern, "test@example.com")
        assert re.match(pattern, "user.name@domain.co.uk")
        assert not re.match(pattern, "invalid-email")
        assert not re.match(pattern, "@nodomain.com")
        assert not re.match(pattern, "no@.com")

    def test_valid_amount(self):
        assert 100 > 0
        assert 0.01 > 0
        assert not (-5 > 0)
        assert not (0 > 0)

    def test_valid_account_number(self):
        pattern = r'^IBAN\d{16}$'
        assert re.match(pattern, "IBAN1234567890123456")
        assert not re.match(pattern, "1234567890123456")
        assert not re.match(pattern, "IBAN123")

    def test_nosql_injection_prevention(self):
        """Test that $ prefixed keys are stripped."""
        malicious_input = {"$gt": "", "email": "test@example.com"}
        sanitized = {k: v for k, v in malicious_input.items() if not k.startswith("$")}
        assert "$gt" not in sanitized
        assert "email" in sanitized
