from flask import Blueprint, make_response, request, jsonify
from flask_restful import Resource, Api
from models import Student, User, db, FeeBalance, Grade
from datetime import datetime
from flask_jwt_extended import jwt_required
from flask_bcrypt import Bcrypt

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')
bcrypt = Bcrypt()
admin_api = Api(admin_bp)

def check_user_exists(username, email):
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    return existing_user is not None

# Student Management
class CreateStudent(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()

        # Ensure all required fields are provided
        required_fields = ['username', 'email', 'password', 'role', 'first_name', 'last_name', 'date_of_birth', 'current_phase']
        for field in required_fields:
            if field not in data:
                return make_response(jsonify({"msg": f"Missing required field: {field}"}), 400)

        # Check if username or email already exists
        if check_user_exists(data['username'], data['email']):
            return make_response(jsonify({"msg": "Username or email already exists"}), 409)

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

        # Create new User
        try:
            new_user = User(
                username=data.get('username'),
                email=data.get('email'),
                password_hash=hashed_password,
                role=data.get('role')
            )
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"msg": f"Error creating user: {str(e)}"}), 500)

        # Convert date_of_birth string to date object
        try:
            date_of_birth = datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d').date()
        except ValueError:
            return make_response(jsonify({"msg": "Invalid date format for date_of_birth. Use YYYY-MM-DD."}), 400)

        # Create new Student
        try:
            new_student = Student(
                user_id=new_user.id,
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                date_of_birth=date_of_birth,
                current_phase=data.get('current_phase')
            )
            db.session.add(new_student)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"msg": f"Error creating student: {str(e)}"}), 500)

        return make_response(jsonify(new_student.to_dict()), 201)

class StudentManager(Resource):
    @jwt_required()
    def get(self, student_id):
        student = Student.query.get_or_404(student_id)
        return make_response(jsonify(student.to_dict()), 200)

    @jwt_required()
    def put(self, student_id):
        data = request.get_json()
        student = Student.query.get_or_404(student_id)
        student.user_id = data.get('user_id', student.user_id)
        student.first_name = data.get('first_name', student.first_name)
        student.last_name = data.get('last_name', student.last_name)
        student.date_of_birth = datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d') if data.get('date_of_birth') else student.date_of_birth
        student.current_phase = data.get('current_phase', student.current_phase)
        db.session.commit()
        return make_response(jsonify(student.to_dict()), 200)

    @jwt_required()
    def delete(self, student_id):
        student = Student.query.get_or_404(student_id)
        db.session.delete(student)
        db.session.commit()
        return 'Student removed from the database', 204

# Fees Management
class GetStudentFeeBalance(Resource):
    def get(self, student_id):
        fee_balance = FeeBalance.query.filter_by(student_id=student_id).first_or_404()
        student = Student.query.get_or_404(student_id)
        balance_remaining = fee_balance.amount_due - fee_balance.amount_paid
        fee_balance_info = {
            "student_name": f"{student.first_name} {student.last_name}",
            "amount_due": fee_balance.amount_due,
            "amount_paid": fee_balance.amount_paid,
            "balance_remaining": balance_remaining,
            "due_date": fee_balance.due_date
        }
        return make_response(jsonify(fee_balance_info), 200)

class FeesManagement(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()

        due_date = datetime.strptime(data.get('due_date'), '%Y-%m-%d').date()

        new_fee_balance = FeeBalance(
            student_id=data.get('student_id'),
            amount_due=data.get('amount_due'),
            amount_paid=data.get('amount_paid'),
            due_date=due_date
        )

        db.session.add(new_fee_balance)
        db.session.commit()
        return make_response(new_fee_balance.to_dict(), 200)

class ManageFeeBalance(Resource):
    @jwt_required()
    def put(self, fee_balance_id):
        data = request.get_json()
        balance = FeeBalance.query.get_or_404(fee_balance_id)
        balance.student_id = data.get('student_id', balance.student_id)
        balance.amount_due = data.get('amount_due', balance.amount_due)
        balance.amount_paid = data.get('amount_paid', balance.amount_paid)
        balance.due_date = datetime.strptime(data.get('due_date'), '%Y-%m-%d') if data.get('due_date') else balance.due_date
        db.session.commit()
        return {'msg': 'Updated successfully'}, 200

    @jwt_required()
    def delete(self, fee_balance_id):
        balance = FeeBalance.query.get_or_404(fee_balance_id)
        db.session.delete(balance)
        db.session.commit()
        return 'Balance removed', 204

# Grades Management
class CreateGrade(Resource):
    def get(self):
        grades = Grade.query.all()
        grades_list = [grade.to_dict() for grade in grades]
        return jsonify(grades_list)

    @jwt_required()
    def post(self):
        data = request.get_json()
        new_grades = Grade(
            student_id=data.get('student_id'),
            course_name=data.get('course_name'),
            grade=data.get('grade'),
            term=data.get('term')
        )
        db.session.add(new_grades)
        db.session.commit()
        return make_response(new_grades.to_dict(), 200)

class SpecificGrade(Resource):
    @jwt_required()
    def get(self, student_id):
        grade = Grade.query.filter_by(student_id=student_id).all()
        grades_list = [g.to_dict() for g in grade]
        return make_response(jsonify(grades_list), 200)

class GradeManager(Resource):
    @jwt_required()
    def put(self, grade_id):
        data = request.get_json()
        grade = Grade.query.get_or_404(grade_id)
        grade.student_id = data.get('student_id', grade.student_id)
        grade.course_name = data.get('course_name', grade.course_name)
        grade.grade = data.get('grade', grade.grade)
        grade.term = data.get('term', grade.term)
        db.session.commit()
        return {'msg': 'Updated successfully'}, 200

    @jwt_required()
    def delete(self, grade_id):
        grade = Grade.query.get_or_404(grade_id)
        db.session.delete(grade)
        db.session.commit()
        return {'msg': 'Removed successfully'}, 204

class DeleteUsers(Resource):
    @jwt_required()
    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {'msg': f'User {user_id} removed successfully'}, 204

admin_api.add_resource(CreateStudent, '/create_student')
admin_api.add_resource(StudentManager, '/student/<int:student_id>')
admin_api.add_resource(GetStudentFeeBalance, '/get_fee_balance/<int:student_id>')
admin_api.add_resource(ManageFeeBalance, '/manage_balance/<int:fee_balance_id>')
admin_api.add_resource(FeesManagement, '/add_fees')
admin_api.add_resource(DeleteUsers, '/deleteusers/<int:user_id>')
admin_api.add_resource(CreateGrade, '/addgrades')
admin_api.add_resource(SpecificGrade, '/studentgrade/<int:student_id>')
admin_api.add_resource(GradeManager, '/managegrades/<int:grade_id>')