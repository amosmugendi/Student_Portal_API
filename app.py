from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from auth import auth_bp, bcrypt, jwt
from models import db
# from student import student_bp
# from admin import admin_bp
from datetime import timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moringa_students_portal.db'
app.config['SECRET_KEY'] = 'YourSecretKey'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=30)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

CORS(app)

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
jwt.init_app(app)

# Initialize migration
migrate = Migrate(app, db)

# Register blueprints
app.register_blueprint(auth_bp)
# app.register_blueprint(student_bp)
# app.register_blueprint(admin_bp)

# Basic route
@app.route("/")
def home():
    return {"msg": "Welcome to the Moringa Students Portal"}

if __name__ == "__main__":
    app.run(debug=True)