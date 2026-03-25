import datetime
import logging
from pymongo.mongo_client import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DB_URL")

_client = None
_suspicious_collection = None
_transactions_collection = None

AML_THRESHOLD = 10000  # EUR
MAX_TRANSACTIONS_PER_HOUR = 5

def _get_collections():
    global _client, _suspicious_collection, _transactions_collection
    if _suspicious_collection is None:
        if db_url is None:
            return None, None
        _client = MongoClient(db_url)
        db = _client["bank"]
        _suspicious_collection = db["suspicious_transactions"]
        _transactions_collection = db["transactions"]
        _suspicious_collection.create_index("flagged_at")
        _suspicious_collection.create_index("rule")
    return _suspicious_collection, _transactions_collection

def flag_transaction(transaction_data, rule, description):
    """Flag a transaction as suspicious."""
    suspicious_col, _ = _get_collections()
    if suspicious_col is None:
        return
    try:
        entry = {
            "transaction_data": transaction_data,
            "rule": rule,
            "description": description,
            "flagged_at": datetime.datetime.utcnow(),
            "reviewed": False,
        }
        suspicious_col.insert_one(entry)
        logging.warning(f"AML Flag: {rule} - {description}")
    except Exception as e:
        logging.error(f"Failed to flag transaction: {e}")

def check_transaction(sender_account_number, receiver_account_number, amount, reason=""):
    """Run AML checks on a transaction. Returns list of flags."""
    flags = []
    transaction_data = {
        "sender": sender_account_number,
        "receiver": receiver_account_number,
        "amount": amount,
        "reason": reason,
        "timestamp": datetime.datetime.utcnow(),
    }

    # Rule 1: Flag transactions over 10,000 EUR
    if amount > AML_THRESHOLD:
        desc = f"Transaction amount {amount} exceeds threshold {AML_THRESHOLD}"
        flag_transaction(transaction_data, "high_value", desc)
        flags.append(("high_value", desc))

    # Rule 2: Flag more than 5 transactions in 1 hour from same account
    _, trans_col = _get_collections()
    if trans_col is not None:
        one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
        recent_count = trans_col.count_documents({
            "sender": sender_account_number,
            "time_stamp": {"$gte": one_hour_ago}
        })
        if recent_count >= MAX_TRANSACTIONS_PER_HOUR:
            desc = f"Account {sender_account_number} has {recent_count} transactions in the last hour"
            flag_transaction(transaction_data, "high_frequency", desc)
            flags.append(("high_frequency", desc))

    # Rule 3: Flag self-transfers
    if sender_account_number == receiver_account_number:
        desc = f"Self-transfer detected for account {sender_account_number}"
        flag_transaction(transaction_data, "self_transfer", desc)
        flags.append(("self_transfer", desc))

    return flags
