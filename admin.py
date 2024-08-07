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

def check_admin_role():
    user_identity = get_jwt_identity()
    user = User.query.get(user_identity)
    if user is None or user.role != 'admin':
        return False
    return True

# Student Management
class GetStudents(Resource):
    @jwt_required()
    def get(self):
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
        students = Student.query.all()
        student_list = [student.to_dict() for student in students]
        return jsonify(student_list)

class CreateStudent(Resource):
    @jwt_required()
    def post(self):
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
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
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
        data = request.get_json()
        student = Student.query.get_or_404(student_id)
        # student.user_id = data.get('user_id')
        student.first_name = data.get('first_name')
        student.last_name = data.get('last_name')
        student.date_of_birth = datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d')
        student.course_id = data.get('course_id')
        student.current_phase = data.get('current_phase')
        db.session.commit()
        return make_response(student.to_dict(), 200)

    @jwt_required()
    def delete(self, student_id):
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
        student = Student.query.get_or_404(student_id)
        db.session.delete(student)
        db.session.commit()
        return 'Student removed from the database', 204

# Fees Management
class GetStudentFeeBalance(Resource):
    @jwt_required()
    def get(self, student_id):
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
        fee_balance = FeeBalance.query.get_or_404(student_id)
        return make_response(fee_balance.to_dict(), 200)

class FeesManagement(Resource):
    @jwt_required()
    def post(self):
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
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
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
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
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
        balance = FeeBalance.query.get_or_404(fee_balance_id)
        db.session.delete(balance)
        db.session.commit()
        return 'Balance removed'

# Grades Management
class CreateGrade(Resource):
    @jwt_required()
    def get(self):
        grades = Grade.query.all()
        grades_list = [grade.to_dict() for grade in grades]
        return  jsonify(grades_list)
    
    @jwt_required()
    def post(self):
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
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
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
        grade = Grade.query.get_or_404(student_id)
        return make_response(grade.to_dict(), 200)

class GradeManager(Resource):
    @jwt_required()
    def put(self, grade_id):
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
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
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
        grade = Grade.query.get_or_404(grade_id)
        db.session.delete(grade)
        db.session.commit()
        return {'msg': 'Removed successfully'}

# Admin Management
class CreateAdmin(Resource):
    @jwt_required()
    def post(self):
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
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
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
        data = request.get_json()
        admin = Admin.query.get_or_404(admin_id)
        admin.user_id = data.get('user_id')
        admin.first_name = data.get('first_name')
        admin.second_name = data.get('second_name')
        db.session.commit()
        return {'msg': 'Upgraded successfully'}

    @jwt_required()
    def delete(self, admin_id):
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
        admin = Admin.query.get_or_404(admin_id)
        db.session.delete(admin)
        db.session.commit()
        return {"msg": "Removed Successfully"}

class DeleteUsers(Resource):
    @jwt_required()
    def delete(self, user_id):
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {'msg': f'User {user_id} removed successfully'}

# Course Management
class CourseResource(Resource):
    @jwt_required()
    def get(self):
        courses = Course.query.all()
        courses_list = [course.to_dict() for course in courses]
        return jsonify(courses_list)
    
    @jwt_required()
    def post(self):
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
        data = request.get_json()
        new_course = Course(
            name=data.get('name'),
            description=data.get('description')
        )
        db.session.add(new_course)
        db.session.commit()
        return make_response(new_course.to_dict(), 200)

class CourseDetailResource(Resource):
    @jwt_required()
    def put(self, course_id):
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
        data = request.get_json()
        course = Course.query.get_or_404(course_id)
        course.name = data.get('name')
        course.description = data.get('description')
        db.session.commit()
        return make_response(course.to_dict(), 200)

    @jwt_required()
    def delete(self, course_id):
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
        course = Course.query.get_or_404(course_id)
        db.session.delete(course)
        db.session.commit()
        return {'msg': 'Course removed successfully'}

# Unit Management
class UnitResource(Resource):
    @jwt_required()
    def post(self):
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
        data = request.get_json()
        new_unit = Unit(
            name=data.get('name'),
            description=data.get('description')
        )
        db.session.add(new_unit)
        db.session.commit()
        return make_response(new_unit.to_dict(), 200)

class UnitDetailResource(Resource):
    @jwt_required()
    def put(self, unit_id):
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
        data = request.get_json()
        unit = Unit.query.get_or_404(unit_id)
        unit.name = data.get('name')
        unit.description = data.get('description')
        db.session.commit()
        return make_response(unit.to_dict(), 200)

    @jwt_required()
    def delete(self, unit_id):
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
        unit = Unit.query.get_or_404(unit_id)
        db.session.delete(unit)
        db.session.commit()
        return {'msg': 'Unit removed successfully'}

# Course Unit Management
class CourseUnitResource(Resource):
    @jwt_required()
    def post(self):
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
        data = request.get_json()
        new_course_unit = CourseUnit(
            course_id=data.get('course_id'),
            unit_id=data.get('unit_id'),
            phase=data.get('phase')
        )
        db.session.add(new_course_unit)
        db.session.commit()
        return make_response(new_course_unit.to_dict(), 200)

class CourseUnitDetailResource(Resource):
    @jwt_required()
    def put(self, course_unit_id):
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
        data = request.get_json()
        course_unit = CourseUnit.query.get_or_404(course_unit_id)
        course_unit.course_id = data.get('course_id')
        course_unit.unit_id = data.get('unit_id')
        course_unit.phase = data.get('phase')
        db.session.commit()
        return make_response(course_unit.to_dict(), 200)

    @jwt_required()
    def delete(self, course_unit_id):
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
        course_unit = CourseUnit.query.get_or_404(course_unit_id)
        db.session.delete(course_unit)
        db.session.commit()
        return {'msg': 'Course Unit removed successfully'}

# New Routes for Admin Details and Student Count
class AdminDetails(Resource):
    @jwt_required()
    def get(self, user_id):
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
        admin = Admin.query.filter_by(user_id=user_id).first_or_404()
        return make_response(admin.to_dict(), 200)
class StudentCount(Resource):
    @jwt_required()
    def get(self):
        if not check_admin_role():
            return make_response(jsonify({"msg": "Access denied: Admins only"}), 403)
        student_count = Student.query.count()
        return make_response({"student_count": student_count}, 200)

admin_api.add_resource(GetStudents, '/students')
admin_api.add_resource(CreateStudent, '/students/create')
admin_api.add_resource(StudentManager, '/students/<int:student_id>')

admin_api.add_resource(GetStudentFeeBalance, '/fee_balance/<int:student_id>')
admin_api.add_resource(FeesManagement, '/fees/create')
admin_api.add_resource(ManageFeeBalance, '/fees/<int:fee_balance_id>')

admin_api.add_resource(CreateGrade, '/grades')
admin_api.add_resource(SpecificGrade, '/grades/<int:student_id>')
admin_api.add_resource(GradeManager, '/grades/<int:grade_id>')

admin_api.add_resource(CreateAdmin, '/admins/create')
admin_api.add_resource(AdminManager, '/admins/<int:admin_id>')
admin_api.add_resource(DeleteUsers, '/users/<int:user_id>')

admin_api.add_resource(CourseResource, '/courses')
admin_api.add_resource(CourseDetailResource, '/courses/<int:course_id>')

admin_api.add_resource(UnitResource, '/units')
admin_api.add_resource(UnitDetailResource, '/units/<int:unit_id>')

admin_api.add_resource(CourseUnitResource, '/course_units')
admin_api.add_resource(CourseUnitDetailResource, '/course_units/<int:course_unit_id>')

admin_api.add_resource(AdminDetails, '/admins/<int:user_id>/details')
admin_api.add_resource(StudentCount, '/students/count')