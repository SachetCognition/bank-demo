import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def _get_fernet():
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        raise ValueError("ENCRYPTION_KEY environment variable is not set")
    # Derive a proper Fernet key from the provided key
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"martian-bank-salt",
        iterations=100000,
    )
    derived_key = base64.urlsafe_b64encode(kdf.derive(key.encode()))
    return Fernet(derived_key)

def encrypt_value(value):
    """Encrypt a string value."""
    if not value:
        return value
    f = _get_fernet()
    return f.encrypt(value.encode()).decode()

def decrypt_value(encrypted_value):
    """Decrypt an encrypted string value."""
    if not encrypted_value:
        return encrypted_value
    f = _get_fernet()
    return f.decrypt(encrypted_value.encode()).decode()

def mask_value(value):
    """Show only last 4 characters."""
    if not value or len(value) <= 4:
        return "****"
    return "*" * (len(value) - 4) + value[-4:]
