# Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import re
from marshmallow import Schema, fields, validate, ValidationError, pre_load

VALID_ACCOUNT_TYPES = ["Checking", "Savings", "Money Market", "Investment"]
VALID_GOVT_ID_TYPES = ["SSN", "Passport", "Driver License", "State ID"]

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
ACCOUNT_NUMBER_REGEX = r'^IBAN\d{16}$'


def sanitize_string(value):
    """Remove potentially dangerous characters for NoSQL injection prevention."""
    if value is None:
        return value
    if isinstance(value, str):
        dangerous_patterns = ['$', '{', '}']
        for pattern in dangerous_patterns:
            value = value.replace(pattern, '')
        return value.strip()
    return value


def sanitize_dict(data):
    """Recursively sanitize dictionary values to prevent NoSQL injection."""
    if data is None:
        return data
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            sanitized_key = sanitize_string(key) if isinstance(key, str) else key
            if sanitized_key and not str(sanitized_key).startswith('$'):
                sanitized[sanitized_key] = sanitize_dict(value)
        return sanitized
    if isinstance(data, list):
        return [sanitize_dict(item) for item in data]
    if isinstance(data, str):
        return sanitize_string(data)
    return data


class SanitizingSchema(Schema):
    """Base schema that sanitizes input before validation."""
    
    @pre_load
    def sanitize_input(self, data, **kwargs):
        return sanitize_dict(data)


class CreateAccountSchema(SanitizingSchema):
    email_id = fields.Email(
        required=True,
        validate=validate.Length(max=255),
        error_messages={
            "required": "Email is required",
            "invalid": "Please provide a valid email address"
        }
    )
    account_type = fields.String(
        required=True,
        validate=validate.OneOf(VALID_ACCOUNT_TYPES),
        error_messages={
            "required": "Account type is required",
            "validator_failed": f"Account type must be one of: {', '.join(VALID_ACCOUNT_TYPES)}"
        }
    )
    address = fields.String(
        required=True,
        validate=[validate.Length(min=5, max=500)],
        error_messages={
            "required": "Address is required",
            "validator_failed": "Address must be between 5 and 500 characters"
        }
    )
    govt_id_number = fields.String(
        required=True,
        validate=[validate.Length(min=4, max=50)],
        error_messages={
            "required": "Government ID number is required",
            "validator_failed": "Government ID number must be between 4 and 50 characters"
        }
    )
    government_id_type = fields.String(
        required=True,
        validate=validate.OneOf(VALID_GOVT_ID_TYPES),
        error_messages={
            "required": "Government ID type is required",
            "validator_failed": f"Government ID type must be one of: {', '.join(VALID_GOVT_ID_TYPES)}"
        }
    )
    name = fields.String(
        required=True,
        validate=[validate.Length(min=2, max=100)],
        error_messages={
            "required": "Name is required",
            "validator_failed": "Name must be between 2 and 100 characters"
        }
    )


class GetAccountDetailSchema(SanitizingSchema):
    account_number = fields.String(
        required=True,
        validate=[validate.Regexp(ACCOUNT_NUMBER_REGEX, error="Invalid account number format")],
        error_messages={
            "required": "Account number is required"
        }
    )


class GetAccountsSchema(SanitizingSchema):
    email_id = fields.Email(
        required=True,
        validate=validate.Length(max=255),
        error_messages={
            "required": "Email is required",
            "invalid": "Please provide a valid email address"
        }
    )


def validate_create_account(data):
    """Validate create account request data."""
    schema = CreateAccountSchema()
    return schema.load(data)


def validate_get_account_detail(data):
    """Validate get account detail request data."""
    schema = GetAccountDetailSchema()
    return schema.load(data)


def validate_get_accounts(data):
    """Validate get accounts request data."""
    schema = GetAccountsSchema()
    return schema.load(data)
