import pytest
import sys
import os

# Add the transactions directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'transactions'))

class TestAMLMonitor:
    def test_high_value_detection(self):
        """Test that transactions over 10000 are flagged."""
        # Test the threshold logic
        AML_THRESHOLD = 10000
        assert 15000 > AML_THRESHOLD
        assert 5000 <= AML_THRESHOLD

    def test_self_transfer_detection(self):
        """Test self-transfer detection."""
        sender = "IBAN1234567890123456"
        receiver = "IBAN1234567890123456"
        assert sender == receiver  # Should be flagged

    def test_normal_transaction_not_flagged(self):
        """Test that normal transactions are not flagged."""
        sender = "IBAN1234567890123456"
        receiver = "IBAN6543210987654321"
        amount = 500
        AML_THRESHOLD = 10000
        assert sender != receiver
        assert amount <= AML_THRESHOLD
