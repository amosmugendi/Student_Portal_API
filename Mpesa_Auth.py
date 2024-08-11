from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource
import requests
import base64
import os
import jwt
from functools import wraps

mpesa_auth_bp = Blueprint('mpesa_auth_bp', __name__, url_prefix='/api/auth')
mpesa_auth_api = Api(mpesa_auth_bp)

# RBAC decorator (if needed)
def allow(*allowed_roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            current_user = getattr(request, 'user', None)
            if current_user and current_user['role'] in allowed_roles:
                return fn(*args, **kwargs)
            return jsonify({"msg": "Access Denied"}), 403
        return decorator
    return wrapper

# Authentication token decorator
def authenticate_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return f(*args, **kwargs)  # No token, proceed without setting request.user

        try:
            secret_key = os.getenv('SECRET_KEY')
            user = jwt.decode(token, secret_key, algorithms=["HS256"])
            request.user = user  # Set request.user with user information
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated_function

class GenerateToken(Resource):
    def get(self):
        try:
            consumer_key = os.getenv('MPESA_CONSUMER_KEY')
            consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')
            auth = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode('utf-8')).decode('utf-8')

            response = requests.get(
                "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
                headers={
                    "Authorization": f"Basic {auth}"
                }
            )
            
            if response.status_code == 200:
                token = response.json().get('access_token')
                return jsonify({"access_token": token}), 200
            else:
                return jsonify({"error": "Failed to generate token"}), response.status_code

        except Exception as e:
            print(f"Error generating token: {e}")
            return jsonify({"error": "Internal server error"}), 500

class ProtectedRoute(Resource):
    @authenticate_token
    def get(self):
        return jsonify({"message": "You have access to this protected route!"}), 200

# Add resources to the API
mpesa_auth_api.add_resource(GenerateToken, '/generate_token')
mpesa_auth_api.add_resource(ProtectedRoute, '/protected_route')