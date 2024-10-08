from flask import Blueprint, request, jsonify, make_response
from flask_restful import Resource, Api
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models import Student, Grade, FeeBalance, Payment, Course, CourseUnit, Unit, db, User
from flask import jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Student, Payment, FeeBalance, db

# Initialize the Blueprint with the import_name argument
students_bp = Blueprint('students_bp', __name__, url_prefix='/students')
students_api = Api(students_bp)

class StudentDashboard(Resource):
    @jwt_required()
    def get(self, user_id):
        student = Student.query.filter_by(user_id=user_id).first_or_404()
        grades = Grade.query.filter_by(student_id=student.id).all()
        fee_balance = FeeBalance.query.filter_by(student_id=student.id).first()
        
        # Fetch the course information from the Student model
        enrolled_course = student.course.to_dict() if student.course else None
        
        return jsonify({
            "student": student.to_dict(),
            "grades": [grade.to_dict() for grade in grades],
            "fee_balance": fee_balance.to_dict() if fee_balance else None,
            "enrolled_course": enrolled_course,
            "current_phase": student.current_phase
        })

class StudentGrades(Resource):
    @jwt_required()
    def get(self, user_id):
        student = Student.query.filter_by(user_id=user_id).first_or_404()
        grades = Grade.query.filter_by(student_id=student.id).all()
        return jsonify([grade.to_dict() for grade in grades])

class StudentFees(Resource):
    @jwt_required()
    def get(self, user_id):
        student = Student.query.filter_by(user_id=user_id).first_or_404()
        fee_balance = FeeBalance.query.filter_by(student_id=student.id).first()
        if fee_balance is None:
            return jsonify({"message": "Fee balance not found"}), 404
        return jsonify(fee_balance.to_dict())

class StudentPhase(Resource):
    @jwt_required()
    def get(self, user_id):
        student = Student.query.filter_by(user_id=user_id).first_or_404()
        return jsonify({"current_phase": student.current_phase})

class StudentProfile(Resource):
    @jwt_required()
    def put(self, user_id):
        student = Student.query.filter_by(user_id=user_id).first_or_404()
        data = request.get_json()
        
        if 'first_name' in data:
            student.first_name = data['first_name']
        if 'last_name' in data:
            student.last_name = data['last_name']
        if 'date_of_birth' in data:
            student.date_of_birth = datetime.fromisoformat(data['date_of_birth'])
        if 'current_phase' in data:
            student.current_phase = data['current_phase']
        
        db.session.commit()
        return jsonify(student.to_dict())

class GetStudentPayments(Resource):
    @jwt_required()
    def get(self):
        current_student_id = get_jwt_identity()
        student = Student.query.get(current_student_id)
        
        if not student:
            return {"msg": "Student not found"}, 404

        payments = Payment.query.filter_by(student_id=current_student_id).all()
        
        payments_list = [payment.to_dict() for payment in payments]
        return jsonify(payments_list)

class StudentPayments(Resource):
    @jwt_required()
    def get(self, user_id):
        payments = Payment.query.filter_by(student_id=user_id).all()
        if not payments:
            return jsonify([])  # Return an empty list instead of a message
        
        payments_data = [
            {
                'student_id': payment.student_id,
                'payment_date': payment.payment_date.isoformat(),
                'transaction_id': payment.id,
                'amount': payment.amount,
                'description': payment.description
            } for payment in payments
        ]
        
        return jsonify(payments_data)

class DeletePayment(Resource):
    @jwt_required()
    def delete(self, user_id, payment_id):
        student = Student.query.filter_by(user_id=user_id).first_or_404()
        payment = Payment.query.filter_by(id=payment_id, student_id=student.id).first_or_404()
        
        fee_balance = FeeBalance.query.filter_by(student_id=student.id).first()
        if fee_balance is None:
            return jsonify({"message": "Fee balance not found"}), 404
        
        db.session.delete(payment)
        
        fee_balance.amount_paid -= payment.amount
        db.session.commit()
        
        return jsonify({"message": "Payment deleted successfully"})

class StudentTransactionHistory(Resource):
    @jwt_required()
    def get(self, user_id):
        student = Student.query.filter_by(user_id=user_id).first_or_404()
        payments = Payment.query.filter_by(student_id=student.id).all()

        if not payments:
            return jsonify([])  # Return an empty list instead of a message

        transactions = [{
            "payment_date": payment.payment_date.isoformat(),
            "description": payment.description,
            "amount": payment.amount
        } for payment in payments]

        return jsonify(transactions)


class PaymentReminder(Resource):
    @jwt_required()
    def get(self, user_id):
        try:
            student = Student.query.filter_by(user_id=user_id).first_or_404()

            fee_balances = FeeBalance.query.filter_by(student_id=student.id).all()

            if not fee_balances:
                return jsonify({
                    "upcomingPayments": [],
                    "message": "No upcoming payments found"
                }), 404

            upcoming_payments = [{
                "due_date": fee_balance.due_date.isoformat(),
                "amount_due": fee_balance.amount_due,
                "amount_paid": fee_balance.amount_paid,
                "remaining_balance": fee_balance.amount_due - fee_balance.amount_paid
            } for fee_balance in fee_balances]

            return jsonify({
                "upcomingPayments": upcoming_payments
            })

        except Exception as e:
            print(f"An error occurred: {e}")
            return jsonify({
                "message": "An internal server error occurred"
            }), 500
                

class UnitsByCourseResource(Resource):
    @jwt_required()  # Requires the user to be logged in
    def get(self, user_id):
        # Fetch the user from the database using the provided user_id
        user = User.query.get(user_id)
        
        if not user:
            return {"error": "User not found"}, 404
        
        # Fetch the student associated with this user
        student = Student.query.filter_by(user_id=user.id).first()
        
        if not student:
            return {"error": "Student not found"}, 404
        
        # Get the course associated with the specified student
        course = Course.query.get(student.course_id)
        
        if not course:
            return {"error": "No course associated with this student"}, 404
        
        # Query to get all units associated with the student's course
        units = (db.session.query(Unit)
                 .join(CourseUnit, Unit.id == CourseUnit.unit_id)
                 .filter(CourseUnit.course_id == course.id)
                 .all())
        
        # Serialize the course and units
        course_data = course.to_dict()  # Assuming Course model has a to_dict() method
        unit_data = [unit.to_dict() for unit in units]
        
        # Return the course and its associated units
        return {
            "course": course_data,
            "units": unit_data
        }, 200


students_api.add_resource(StudentDashboard, '/<int:user_id>/dashboard')
students_api.add_resource(StudentGrades, '/<int:user_id>/grades')
students_api.add_resource(StudentFees, '/<int:user_id>/fees')
students_api.add_resource(StudentPhase, '/<int:user_id>/phase')
students_api.add_resource(StudentProfile, '/<int:user_id>/profile')
students_api.add_resource(StudentPayments, '/<int:user_id>/payments')
students_api.add_resource(DeletePayment, '/<int:user_id>/payments/<int:payment_id>')
students_api.add_resource(GetStudentPayments, '/payments')
students_api.add_resource(StudentTransactionHistory, '/<int:user_id>/transaction_history')
students_api.add_resource(PaymentReminder, '/<int:user_id>/payment-reminder')
students_api.add_resource(UnitsByCourseResource, '/units-by-course/<int:user_id>')