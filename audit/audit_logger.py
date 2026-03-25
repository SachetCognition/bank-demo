import os
import datetime
import logging
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DB_URL")

_client = None
_collection = None

def _get_collection():
    global _client, _collection
    if _collection is None:
        if db_url is None:
            logging.warning("DB_URL not set, audit logging disabled")
            return None
        _client = MongoClient(db_url)
        db = _client["bank"]
        _collection = db["audit_log"]
        _collection.create_index("timestamp")
        _collection.create_index("action")
        _collection.create_index("user_email")
        _collection.create_index("service_name")
    return _collection

def log_audit(action, user_email, details, ip_address="unknown", service_name="unknown"):
    """Log an audit entry. Entries are immutable - no update/delete exposed."""
    try:
        collection = _get_collection()
        if collection is None:
            return
        entry = {
            "timestamp": datetime.datetime.utcnow(),
            "action": action,
            "user_email": user_email,
            "details": details,
            "ip_address": ip_address,
            "service_name": service_name,
        }
        collection.insert_one(entry)
        logging.debug(f"Audit log: {action} by {user_email}")
    except Exception as e:
        logging.error(f"Failed to write audit log: {e}")
