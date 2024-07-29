from flask import Blueprint
from flask_restful import Api, Resource, reqparse
from models import User, db
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, JWTManager
from functools import wraps

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')
bcrypt = Bcrypt()
jwt = JWTManager()
auth_api = Api(auth_bp)

# RBAC decorator
def allow(*allowed_roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            if user and user.role in allowed_roles:
                return fn(*args, **kwargs)
            return {"msg": "Access Denied"}, 403
        return decorator
    return wrapper

# User loader callback for JWT
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).first()

# Request parsers
login_args = reqparse.RequestParser()
login_args.add_argument('email', type=str, help='Email is required', required=True)
login_args.add_argument('password', type=str, help='Password is required', required=True)

# Resource classes
class Login(Resource):
    def post(self):
        data = login_args.parse_args()
        user = User.query.filter_by(email=data['email']).first()
        if user and bcrypt.check_password_hash(user.password_hash, data['password']):
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            role = user.role  # Assuming each user has one role
            return {"access_token": access_token, "refresh_token": refresh_token, "role": role}, 200
        return {"msg": "Invalid credentials"}, 401

class RefreshToken(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_id)
        return {"access_token": new_access_token}, 200

# Routes setup
auth_api.add_resource(Login, '/login')
auth_api.add_resource(RefreshToken, '/refresh')