from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from auth import auth_bp, bcrypt, jwt
from models import db
from admin import admin_bp
from students import students_bp  # Import the students blueprint
from payment import payment_bp  # Import the payment blueprint
from datetime import timedelta
from flask_mail import Mail

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moringa_students_portal.db'
app.config['SECRET_KEY'] = 'MoringaStudents'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=100)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

CORS(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587 
app.config['MAIL_USERNAME'] = 'moringaportal@gmail.com'
app.config['MAIL_PASSWORD'] = 'fqfk eeie oosg eems'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
jwt.init_app(app)

# Initialize migration
migrate = Migrate(app, db)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(students_bp)  # Register the students blueprint
app.register_blueprint(payment_bp)  # Register the payment blueprint
# app.register_blueprint(mpesa_auth_bp)

# Custom response for expired token
@jwt.expired_token_loader
def handle_expired_token(expired_token):
    return {
        'msg': 'Token has expired',
        'error': 'token_expired'
    }, 401

# Basic route
@app.route("/")
def home():
    return {"msg": "Welcome to the Moringa Students Portal"}

if __name__ == "__main__":
    app.run(debug=True)
