from flask import Blueprint,make_response,request,jsonify
from flask_restful import Resource,Api
from models import Student,User,db,FeeBalance
from datetime import datetime
from flask_jwt_extended import jwt_required
from flask_bcrypt import Bcrypt

admin_bp = Blueprint('admin_bp',__name__,url_prefix='/admin')
bcrypt = Bcrypt()
admin_api = Api(admin_bp)

def check_user_exists(username, email):
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    return existing_user is not None

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

class DeleteStudent(Resource):
    jwt_required()
    def delete(self,student_id):
        student = Student.query.get_or_404(student_id)
        db.session.delete(student)
        db.session.commit()
        return 'Student removed from the database',204

class GetStudentFeeBalance(Resource):
    def get(self,student_id):
        fee_balance = FeeBalance.query.get_or_404(student_id)
        return make_response(fee_balance.to_dict(), 200)

class FeesManagement(Resource):
    jwt_required()
    def post(self):
        data = request.get_json()

        due_date = datetime.strptime(data.get('due_date'), '%Y-%m-%d').date()

        new_fee_balance = FeeBalance(
        student_id = data.get('student_id'),
        amount_due = data.get('amount_due'),
        amount_paid = data.get('amount_paid'),
        due_date = due_date
        )

        db.session.add(new_fee_balance)
        db.session.commit()
        return make_response(new_fee_balance.to_dict(), 200)

class DeleteFeeBalance(Resource):
    jwt_required()
    def delete(self, fee_balance_id):
        balance = FeeBalance.query.get_or_404(fee_balance_id)
        db.session.delete(balance)
        db.session.commit()
        return 'Balance removed'

class DeleteUsers(Resource):
    jwt_required()
    def delete(self,user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return f'User {user_id} removed successfuly'
    

    
admin_api.add_resource(CreateStudent, '/create_student')
admin_api.add_resource(DeleteStudent, '/delete_student/<int:student_id>')
admin_api.add_resource(GetStudentFeeBalance, '/feebalance/<int:student_id>')
admin_api.add_resource(DeleteFeeBalance, '/deletebalance/<int:fee_balance_id>')
admin_api.add_resource(FeesManagement, '/fees')
admin_api.add_resource(DeleteUsers, '/deleteusers/<int:user_id>')