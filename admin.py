from flask import Blueprint, make_response, request, jsonify
from flask_restful import Resource, Api
from models import Student, User, db, FeeBalance, Grade, Admin, Course, Unit, CourseUnit
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
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
                course_id=data.get('course_id'),
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
    def put(self, student_id):
        data = request.get_json()
        student = Student.query.get_or_404(student_id)
        student.user_id = data.get('user_id')
        student.first_name = data.get('first_name')
        student.last_name = data.get('last_name')
        student.date_of_birth = datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d')
        student.course_id = data.get('course_id')
        student.current_phase = data.get('current_pahse')
        db.session.commit()
        return make_response(student.to_dict(), 200)

    @jwt_required()
    def delete(self, student_id):
        student = Student.query.get_or_404(student_id)
        db.session.delete(student)
        db.session.commit()
        return 'Student removed from the database', 204

# Fees Management
class GetStudentFeeBalance(Resource):
    def get(self, student_id):
        fee_balance = FeeBalance.query.get_or_404(student_id)
        return make_response(fee_balance.to_dict(), 200)

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
        balance.student_id = data.get('student_id')
        balance.amount_due = data.get('amount_due')
        balance.amount_paid = data.get('amount_paid')
        balance.due_date = datetime.strptime(data.get('due_date'), '%Y-%m-%d')
        db.session.commit()
        return {'msg': 'Updated successfully'}, 200
    
    @jwt_required()
    def delete(self, fee_balance_id):
        balance = FeeBalance.query.get_or_404(fee_balance_id)
        db.session.delete(balance)
        db.session.commit()
        return 'Balance removed'

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
            course_unit_id=data.get('course_unit_id'),
            grade=data.get('grade'),
            phase=data.get('phase')
        )
        db.session.add(new_grades)
        db.session.commit()
        return make_response(new_grades.to_dict(), 200)

class SpecificGrade(Resource):
    @jwt_required()
    def get(self, student_id):
        grade = Grade.query.get_or_404(student_id)
        return make_response(grade.to_dict(), 200)
    
class GradeManager(Resource):
    @jwt_required()
    def put(self, grade_id):
        data = request.get_json()
        grade = Grade.query.get_or_404(grade_id)
        grade.student_id = data.get('student_id')
        grade.course_unit_id = data.get('course_unit_id')
        grade.grade = data.get('grade')
        grade.phase = data.get('phase')
        db.session.commit()
        return {'msg': 'Upgraded successfully'}

    @jwt_required()
    def delete(self, grade_id):
        grade = Grade.query.get_or_404(grade_id)
        db.session.delete(grade)
        db.session.commit()
        return {'msg': 'Removed successfully'}

# Admin Management
class CreateAdmin(Resource):
    def post(self):
        data = request.get_json()

        # Ensure all required fields are provided
        required_fields = ['username', 'email', 'password', 'role', 'first_name', 'last_name']
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

        # Create new Admin
        try:
            new_admin = Admin(
                user_id=new_user.id,
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
            )
            db.session.add(new_admin)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"msg": f"Error creating admin: {str(e)}"}), 500)

        return make_response(jsonify(new_admin.to_dict()), 201)
    
class AdminManager(Resource):
    @jwt_required()
    def put(self, admin_id):
        data = request.get_json()
        admin = Admin.query.get_or_404(admin_id)
        admin.user_id = data.get('user_id')
        admin.first_name = data.get('first_name')
        admin.second_name = data.get('second_name')
        db.session.commit()
        return {'msg': 'Upgraded successfully'}
    
    @jwt_required()
    def delete(self, admin_id):
        admin = Admin.query.get_or_404(admin_id)
        db.session.delete(admin)
        db.session.commit()
        return {"msg": "Removed Successfully"}

class DeleteUsers(Resource):
    @jwt_required()
    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {'msg': f'User {user_id} removed successfully'}
    
# Course Management
class CourseResource(Resource):
    def get(self):
        courses = Course.query.all()
        courses_list = [course.to_dict() for course in courses]
        return jsonify(courses_list)
    
    @jwt_required()
    def post(self):
        data = request.get_json()
        new_course = Course(
            course_name=data.get('name'),
            fee=data.get('fee')
            
        )
        db.session.add(new_course)
        db.session.commit()
        return make_response(new_course.to_dict(), 200)

class CourseManager(Resource):
    @jwt_required()
    def put(self, course_id):
        data = request.get_json()
        course = Course.query.get_or_404(course_id)
        course.course_name = data.get('name')
        course.fee = data.get('fee')
        db.session.commit()
        return {'msg': 'Updated successfully'}
    
    @jwt_required()
    def delete(self, course_id):
        course = Course.query.get_or_404(course_id)
        db.session.delete(course)
        db.session.commit()
        return {'msg': f'Course with id {course_id} has been removed'}

# Unit Management
class UnitResource(Resource):
    def get(self):
        units = Unit.query.all()
        units_list = [unit.to_dict() for unit in units]
        return jsonify(units_list)
    
    @jwt_required()
    def post(self):
        data = request.get_json()
        new_unit = Unit(
            unit_name=data.get('unit_name')
        )
        db.session.add(new_unit)
        db.session.commit()
        return make_response(new_unit.to_dict(), 200)

class UnitManager(Resource):
    @jwt_required()
    def put(self, unit_id):
        data = request.get_json()
        unit = Unit.query.get_or_404(unit_id)
        unit.unit_name = data.get('unit_name')
        db.session.commit()
        return {'msg': 'Updated successfully'}
    
    @jwt_required()
    def delete(self, unit_id):
        unit = Unit.query.get_or_404(unit_id)
        db.session.delete(unit)
        db.session.commit()
        return {'msg': f'Unit with id {unit_id} has been removed'}

# CourseUnit Management
class CourseUnitResource(Resource):
    def get(self):
        course_units = CourseUnit.query.all()
        course_units_list = [course_unit.to_dict() for course_unit in course_units]
        return jsonify(course_units_list)
    
    @jwt_required()
    def post(self):
        data = request.get_json()
        new_course_unit = CourseUnit(
            course_id=data.get('course_id'),
            unit_id=data.get('unit_id'),
            phase=data.get('phase')
        )
        db.session.add(new_course_unit)
        db.session.commit()
        return make_response(new_course_unit.to_dict(), 200)

class CourseUnitManager(Resource):
    @jwt_required()
    def put(self, course_unit_id):
        data = request.get_json()
        course_unit = CourseUnit.query.get_or_404(course_unit_id)
        course_unit.course_id = data.get('course_id')
        course_unit.unit_id = data.get('unit_id')
        course_unit.phase = data.get('phase')
        db.session.commit()
        return {'msg': 'Updated successfully'}
    
    @jwt_required()
    def delete(self, course_unit_id):
        course_unit = CourseUnit.query.get_or_404(course_unit_id)
        db.session.delete(course_unit)
        db.session.commit()
        return {'msg': f'CourseUnit with id {course_unit_id} has been removed'}

admin_api.add_resource(CreateStudent, '/create_student')
admin_api.add_resource(StudentManager, '/manage_student/<int:student_id>')
admin_api.add_resource(GetStudentFeeBalance, '/fee_balance/<int:student_id>')
admin_api.add_resource(FeesManagement, '/add_fee_balance')
admin_api.add_resource(ManageFeeBalance, '/manage_fee_balance/<int:fee_balance_id>')
admin_api.add_resource(CreateGrade, '/add_grades')
admin_api.add_resource(SpecificGrade, '/grade/<int:student_id>')
admin_api.add_resource(GradeManager, '/manage_grade/<int:grade_id>')
admin_api.add_resource(CreateAdmin, '/create_admin')
admin_api.add_resource(AdminManager, '/manage_admin/<int:admin_id>')
admin_api.add_resource(DeleteUsers, '/remove_user/<int:user_id>')
admin_api.add_resource(CourseResource, '/courses')
admin_api.add_resource(CourseManager, '/courses/<int:course_id>')
admin_api.add_resource(UnitManager, '/units/<int:unit_id>')
admin_api.add_resource(UnitResource, '/units')
admin_api.add_resource(CourseUnitResource, '/course_units')
admin_api.add_resource(CourseUnitManager, '/manage_course_unit/<int:course_unit_id>')