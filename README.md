# Moringa Students Portal Backend

This is the backend for the Moringa Students Portal project, which allows Moringa students to create accounts, log in, access their grades, fee balances, and current phase information. Administrators can manage student accounts, update student details, and view all student information.

## Table of Contents

- [Project Structure](#project-structure)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Setup and Installation](#setup-and-installation)
- [Database Migration](#database-migration)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Authentication & Authorization](#authentication--authorization)
- [Contributing](#contributing)
- [License](#license)

## Project Structure

```plaintext
moringa-students-portal-backend/
│
├── app.py
├── config.py
├── instance/
│   └── hospital.db
├── migrations/
│   ├── alembic.ini
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions/
│       └── d008594f6e3f_initial.py
├── models.py
├── requirements.txt
├── seed.py
├── auth/
│   ├── __init__.py
│   ├── auth_routes.py
│   ├── auth_models.py
│   └── auth_utils.py
└── students/
    ├── __init__.py
    ├── student_routes.py
    ├── student_models.py
    └── student_utils.py

##Features
User authentication and authorization using JWT
CRUD operations for user management
Student-specific endpoints for accessing grades, fee balances, and phases
Admin-specific endpoints for managing student information
Password reset functionality for students on first login
Technologies Used
Backend Framework: Flask
Database: PostgreSQL
ORM: SQLAlchemy
Authentication: JWT (JSON Web Tokens)
Others: Flask-Migrate, Flask-CORS, Flask-Bcrypt, Flask-RESTful
Setup and Installation
Clone the repository:

bash
Copy code
git clone https://github.com/yourusername/moringa-students-portal-backend.git
cd moringa-students-portal-backend
Create and activate a virtual environment:

bash
Copy code
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Set up environment variables:

Create a .env file in the root directory and add the following:

plaintext
Copy code
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key
SQLALCHEMY_DATABASE_URI=postgresql://username:password@localhost:5432/yourdatabase
Database Migration
Initialize migration scripts:

bash
Copy code
flask db init
Generate migration scripts:

bash
Copy code
flask db migrate -m "Initial migration."
Apply migrations:

bash
Copy code
flask db upgrade
Environment Variables
FLASK_APP: The entry point of the Flask application.
FLASK_ENV: The environment in which the app is running (development/production).
SECRET_KEY: A secret key for securing sessions.
SQLALCHEMY_DATABASE_URI: The URI for the PostgreSQL database.
Running the Application
Start the Flask application:

bash
Copy code
flask run
The application will be available at http://127.0.0.1:5000/.

API Endpoints
Authentication
POST /auth/login: Log in a user and return access and refresh tokens.
POST /auth/refresh: Refresh the access token using the refresh token.
Students
GET /students/:user_id/dashboard: Get the student dashboard information.
PUT /students/:user_id/change-password: Change the password for the student.
Admin
GET /admin/students: Get a list of all students.
POST /admin/students: Add a new student.
PUT /admin/students/:student_id: Update a student's information.
DELETE /admin/students/:student_id: Deactivate a student's account.
Authentication & Authorization
JWT: Used for securing endpoints.
Roles: Admin and Student roles with specific permissions.
Contributing
Fork the repository.

Create a new branch:

bash
Copy code
git checkout -b feature-name
Make your changes and commit them:

bash
Copy code
git commit -m "Description of changes."
Push to the branch:

bash
Copy code
git push origin feature-name
Create a pull request.

License
This project is licensed under the MIT License.

vbnet
Copy code

Copy the above code and paste it into a file named `README.md` in your project's root directory. This will create a comprehensive README file for your backend project.
