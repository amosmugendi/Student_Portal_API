from flask import Blueprint,make_response,request
from flask_restful import Resource,Api
from models import Student,User,db,FeeBalance
from datetime import datetime
from flask_jwt_extended import jwt_required
from werkzeug.security import generate_password_hash


admin_bp = Blueprint('admin_bp',__name__,url_prefix='/admin')

admin_api = Api(admin_bp)

class CreateStudent(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()

        hashed_password = generate_password_hash(data.get('password'))

        new_user = User(
            username=data.get('username'),
            email=data.get('email'),
            password_hash=hashed_password,
            role = data.get('role')
        )
        db.session.add(new_user)
        db.session.commit()

        date_of_birth = datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d').date()

        new_student = Student(
            user_id=new_user.id,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            date_of_birth=date_of_birth,
            current_phase=data.get('current_phase')
        )
        db.session.add(new_student)
        db.session.commit()

        return make_response(new_student.to_dict(), 201)

class DeleteStudent(Resource):
    jwt_required()
    def delete(self,student_id):
        student = Student.query.get_or_404(student_id)
        db.session.delete(student)
        db.session.commit()
        return 'Student removed from the database',204
    

    
admin_api.add_resource(CreateStudent, '/create_student')
admin_api.add_resource(DeleteStudent, '/delete_student/<int:student_id>')