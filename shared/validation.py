import re


def validate_email(email):
    """Validates email format using regex."""
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_amount(amount):
    """Validates amount > 0."""
    try:
        return float(amount) > 0
    except (TypeError, ValueError):
        return False


def validate_account_number(account_number):
    """Validates expected pattern (starts with 'IBAN' followed by digits)."""
    if not account_number or not isinstance(account_number, str):
        return False
    pattern = r'^IBAN\d+$'
    return bool(re.match(pattern, account_number))


def sanitize_mongo_input(input_data):
    """Strips $ prefixed keys from dicts to prevent NoSQL injection."""
    if isinstance(input_data, dict):
        return {
            k: sanitize_mongo_input(v)
            for k, v in input_data.items()
            if not (isinstance(k, str) and k.startswith('$'))
        }
    elif isinstance(input_data, list):
        return [sanitize_mongo_input(item) for item in input_data]
    return input_data
