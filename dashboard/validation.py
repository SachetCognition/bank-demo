# Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import re
from marshmallow import Schema, fields, validate, ValidationError, pre_load

VALID_ACCOUNT_TYPES = ["Checking", "Savings", "Money Market", "Investment"]
VALID_GOVT_ID_TYPES = ["SSN", "Passport", "Driver License", "State ID"]
VALID_LOAN_TYPES = ["Base Camp", "Rover", "Potato Farming", "Ice Home", "Rocker"]

ACCOUNT_NUMBER_REGEX = r'^IBAN\d{16}$'
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
MONGODB_OBJECTID_REGEX = r'^[0-9a-fA-F]{24}$'
PASSWORD_REGEX = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'

MAX_TRANSACTION_AMOUNT = 1000000.00
MIN_TRANSACTION_AMOUNT = 0.01
MAX_LOAN_AMOUNT = 10000000.00
MIN_LOAN_AMOUNT = 100.00
MAX_INTEREST_RATE = 30.0
MIN_INTEREST_RATE = 0.1


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


def sanitize_form_data(form_data):
    """Sanitize form data from request.form."""
    if form_data is None:
        return {}
    sanitized = {}
    for key in form_data:
        sanitized_key = sanitize_string(key)
        if sanitized_key and not sanitized_key.startswith('$'):
            sanitized[sanitized_key] = sanitize_string(form_data[key])
    return sanitized


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


class GetAccountsSchema(SanitizingSchema):
    email_id = fields.Email(
        required=True,
        validate=validate.Length(max=255),
        error_messages={
            "required": "Email is required",
            "invalid": "Please provide a valid email address"
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


class TransactionSchema(SanitizingSchema):
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
    sender_account_type = fields.String(
        required=True,
        validate=validate.OneOf(VALID_ACCOUNT_TYPES),
        error_messages={
            "required": "Sender account type is required"
        }
    )
    receiver_account_type = fields.String(
        required=True,
        validate=validate.OneOf(VALID_ACCOUNT_TYPES),
        error_messages={
            "required": "Receiver account type is required"
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


class GetTransactionHistorySchema(SanitizingSchema):
    account_number = fields.String(
        required=True,
        validate=[validate.Regexp(ACCOUNT_NUMBER_REGEX, error="Invalid account number format")],
        error_messages={
            "required": "Account number is required"
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


class LoanRequestSchema(SanitizingSchema):
    name = fields.String(
        required=True,
        validate=[validate.Length(min=2, max=100)],
        error_messages={
            "required": "Name is required",
            "validator_failed": "Name must be between 2 and 100 characters"
        }
    )
    email = fields.Email(
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
    account_number = fields.String(
        required=True,
        validate=[validate.Regexp(ACCOUNT_NUMBER_REGEX, error="Invalid account number format")],
        error_messages={
            "required": "Account number is required"
        }
    )
    govt_id_type = fields.String(
        required=True,
        validate=validate.OneOf(VALID_GOVT_ID_TYPES),
        error_messages={
            "required": "Government ID type is required",
            "validator_failed": f"Government ID type must be one of: {', '.join(VALID_GOVT_ID_TYPES)}"
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
    loan_type = fields.String(
        required=True,
        validate=validate.OneOf(VALID_LOAN_TYPES),
        error_messages={
            "required": "Loan type is required",
            "validator_failed": f"Loan type must be one of: {', '.join(VALID_LOAN_TYPES)}"
        }
    )
    loan_amount = fields.Float(
        required=True,
        validate=[
            validate.Range(min=MIN_LOAN_AMOUNT, max=MAX_LOAN_AMOUNT,
                          error=f"Loan amount must be between ${MIN_LOAN_AMOUNT} and ${MAX_LOAN_AMOUNT}")
        ],
        error_messages={
            "required": "Loan amount is required",
            "invalid": "Loan amount must be a valid number"
        }
    )
    interest_rate = fields.Float(
        required=True,
        validate=[
            validate.Range(min=MIN_INTEREST_RATE, max=MAX_INTEREST_RATE,
                          error=f"Interest rate must be between {MIN_INTEREST_RATE}% and {MAX_INTEREST_RATE}%")
        ],
        error_messages={
            "required": "Interest rate is required",
            "invalid": "Interest rate must be a valid number"
        }
    )
    time_period = fields.String(
        required=True,
        validate=[validate.Length(min=1, max=50)],
        error_messages={
            "required": "Time period is required",
            "validator_failed": "Time period must be between 1 and 50 characters"
        }
    )


class LoanHistorySchema(SanitizingSchema):
    email = fields.Email(
        required=True,
        validate=validate.Length(max=255),
        error_messages={
            "required": "Email is required",
            "invalid": "Please provide a valid email address"
        }
    )


class RegisterUserSchema(SanitizingSchema):
    name = fields.String(
        required=True,
        validate=[validate.Length(min=2, max=100)],
        error_messages={
            "required": "Name is required",
            "validator_failed": "Name must be between 2 and 100 characters"
        }
    )
    email = fields.Email(
        required=True,
        validate=validate.Length(max=255),
        error_messages={
            "required": "Email is required",
            "invalid": "Please provide a valid email address"
        }
    )
    password = fields.String(
        required=True,
        validate=[
            validate.Length(min=8, max=128),
            validate.Regexp(PASSWORD_REGEX, error="Password must contain at least one letter, one digit, and one special character (@$!%*#?&)")
        ],
        error_messages={
            "required": "Password is required"
        }
    )


class LoginUserSchema(SanitizingSchema):
    email = fields.Email(
        required=True,
        validate=validate.Length(max=255),
        error_messages={
            "required": "Email is required",
            "invalid": "Please provide a valid email address"
        }
    )
    password = fields.String(
        required=True,
        validate=[validate.Length(min=1, max=128)],
        error_messages={
            "required": "Password is required"
        }
    )


class ProfileUserSchema(SanitizingSchema):
    email = fields.Email(
        required=True,
        validate=validate.Length(max=255),
        error_messages={
            "required": "Email is required",
            "invalid": "Please provide a valid email address"
        }
    )
    password = fields.String(
        required=False,
        validate=[
            validate.Length(min=8, max=128),
            validate.Regexp(PASSWORD_REGEX, error="Password must contain at least one letter, one digit, and one special character (@$!%*#?&)")
        ]
    )


class GetATMsSchema(SanitizingSchema):
    isOpenNow = fields.Boolean(
        required=False,
        load_default=False
    )
    isInterPlanetary = fields.Boolean(
        required=False,
        load_default=False
    )


class GetSpecificATMSchema(SanitizingSchema):
    id = fields.String(
        required=True,
        validate=[validate.Regexp(MONGODB_OBJECTID_REGEX, error="Invalid ATM ID format")],
        error_messages={
            "required": "ATM ID is required"
        }
    )


def validate_create_account(data):
    schema = CreateAccountSchema()
    return schema.load(data)


def validate_get_accounts(data):
    schema = GetAccountsSchema()
    return schema.load(data)


def validate_get_account_detail(data):
    schema = GetAccountDetailSchema()
    return schema.load(data)


def validate_transaction(data):
    schema = TransactionSchema()
    return schema.load(data)


def validate_zelle(data):
    schema = ZelleSchema()
    return schema.load(data)


def validate_get_transaction_history(data):
    schema = GetTransactionHistorySchema()
    return schema.load(data)


def validate_get_transaction_by_id(data):
    schema = GetTransactionByIDSchema()
    return schema.load(data)


def validate_loan_request(data):
    schema = LoanRequestSchema()
    return schema.load(data)


def validate_loan_history(data):
    schema = LoanHistorySchema()
    return schema.load(data)


def validate_register_user(data):
    schema = RegisterUserSchema()
    return schema.load(data)


def validate_login_user(data):
    schema = LoginUserSchema()
    return schema.load(data)


def validate_profile_user(data):
    schema = ProfileUserSchema()
    return schema.load(data)


def validate_get_atms(data):
    schema = GetATMsSchema()
    return schema.load(data)


def validate_get_specific_atm(data):
    schema = GetSpecificATMSchema()
    return schema.load(data)
