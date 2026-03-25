import os
import jwt
from functools import wraps
from flask import request, jsonify

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET environment variable is not set")

def require_jwt(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check cookie first
        token = request.cookies.get("jwt")
        # Then check Authorization header
        if not token:
            auth_header = request.headers.get("Authorization")
            token = auth_header.split(" ", 1)[-1] if auth_header else None
        if not token:
            return jsonify({"message": "Not authorized, no token"}), 401
        try:
            decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            request.user_id = decoded.get("userId")
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Not authorized, token failed"}), 401
        return f(*args, **kwargs)
    return decorated
