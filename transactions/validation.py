# Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import re
from marshmallow import Schema, fields, validate, ValidationError, pre_load, validates

ACCOUNT_NUMBER_REGEX = r'^IBAN\d{16}$'
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
MONGODB_OBJECTID_REGEX = r'^[0-9a-fA-F]{24}$'

MAX_TRANSACTION_AMOUNT = 1000000.00
MIN_TRANSACTION_AMOUNT = 0.01


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


class SendMoneySchema(SanitizingSchema):
    sender_account_number = fields.String(
        required=True,
        validate=[validate.Regexp(ACCOUNT_NUMBER_REGEX, error="Invalid sender account number format")],
        error_messages={
            "required": "Sender account number is required"
        }
    )
    receiver_account_number = fields.String(
        required=True,
        validate=[validate.Regexp(ACCOUNT_NUMBER_REGEX, error="Invalid receiver account number format")],
        error_messages={
            "required": "Receiver account number is required"
        }
    )
    amount = fields.Float(
        required=True,
        validate=[
            validate.Range(min=MIN_TRANSACTION_AMOUNT, max=MAX_TRANSACTION_AMOUNT,
                          error=f"Amount must be between ${MIN_TRANSACTION_AMOUNT} and ${MAX_TRANSACTION_AMOUNT}")
        ],
        error_messages={
            "required": "Amount is required",
            "invalid": "Amount must be a valid number"
        }
    )
    reason = fields.String(
        required=False,
        validate=[validate.Length(max=500)],
        load_default="",
        error_messages={
            "validator_failed": "Reason must not exceed 500 characters"
        }
    )


class ZelleSchema(SanitizingSchema):
    sender_email = fields.Email(
        required=True,
        validate=validate.Length(max=255),
        error_messages={
            "required": "Sender email is required",
            "invalid": "Please provide a valid sender email address"
        }
    )
    receiver_email = fields.Email(
        required=True,
        validate=validate.Length(max=255),
        error_messages={
            "required": "Receiver email is required",
            "invalid": "Please provide a valid receiver email address"
        }
    )
    amount = fields.Float(
        required=True,
        validate=[
            validate.Range(min=MIN_TRANSACTION_AMOUNT, max=MAX_TRANSACTION_AMOUNT,
                          error=f"Amount must be between ${MIN_TRANSACTION_AMOUNT} and ${MAX_TRANSACTION_AMOUNT}")
        ],
        error_messages={
            "required": "Amount is required",
            "invalid": "Amount must be a valid number"
        }
    )
    reason = fields.String(
        required=False,
        validate=[validate.Length(max=500)],
        load_default="",
        error_messages={
            "validator_failed": "Reason must not exceed 500 characters"
        }
    )


class GetTransactionByIDSchema(SanitizingSchema):
    transaction_id = fields.String(
        required=True,
        validate=[validate.Regexp(MONGODB_OBJECTID_REGEX, error="Invalid transaction ID format")],
        error_messages={
            "required": "Transaction ID is required"
        }
    )


class GetTransactionHistorySchema(SanitizingSchema):
    account_number = fields.String(
        required=True,
        validate=[validate.Regexp(ACCOUNT_NUMBER_REGEX, error="Invalid account number format")],
        error_messages={
            "required": "Account number is required"
        }
    )


def validate_send_money(data):
    """Validate send money request data."""
    schema = SendMoneySchema()
    return schema.load(data)


def validate_zelle(data):
    """Validate Zelle transfer request data."""
    schema = ZelleSchema()
    return schema.load(data)


def validate_get_transaction_by_id(data):
    """Validate get transaction by ID request data."""
    schema = GetTransactionByIDSchema()
    return schema.load(data)


def validate_get_transaction_history(data):
    """Validate get transaction history request data."""
    schema = GetTransactionHistorySchema()
    return schema.load(data)
