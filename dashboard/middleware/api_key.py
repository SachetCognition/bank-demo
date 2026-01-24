# Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import os
from functools import wraps
from flask import request, jsonify

# API Key for internal service-to-service communication
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "martianbank-internal-api-key-change-in-production")


def validate_api_key(f):
    """
    Decorator to validate API key for internal service calls.
    Allows requests without API key for backward compatibility.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-Key") or request.headers.get("X-Internal-API-Key")
        
        if api_key:
            if api_key != INTERNAL_API_KEY:
                return jsonify({"message": "Invalid API key"}), 401
            # Mark request as internal call
            request.is_internal_call = True
        else:
            request.is_internal_call = False
        
        return f(*args, **kwargs)
    return decorated_function


def require_api_key(f):
    """
    Decorator to require API key for internal service calls.
    Stricter version that rejects requests without valid API key.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-Key") or request.headers.get("X-Internal-API-Key")
        
        if not api_key:
            return jsonify({"message": "API key required for this endpoint"}), 401
        
        if api_key != INTERNAL_API_KEY:
            return jsonify({"message": "Invalid API key"}), 401
        
        request.is_internal_call = True
        return f(*args, **kwargs)
    return decorated_function


def get_api_key_headers():
    """
    Helper function to get headers with API key for outgoing requests.
    """
    return {
        "X-Internal-API-Key": INTERNAL_API_KEY,
    }
