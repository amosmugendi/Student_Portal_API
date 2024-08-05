from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Student, Grade, FeeBalance, Payment
from datetime import datetime

students_bp = Blueprint('students', __name__)

@students_bp.route('/students/<int:student_id>/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard(student_id):
    student = Student.query.get_or_404(student_id)
    grades = Grade.query.filter_by(student_id=student.id).all()
    fee_balance = FeeBalance.query.filter_by(student_id=student.id).first()
    return jsonify({
        "student": student.to_dict(),
        "grades": [grade.to_dict() for grade in grades],
        "fee_balance": fee_balance.to_dict() if fee_balance else None,
        "current_phase": student.current_phase
    })

@students_bp.route('/students/<int:student_id>/grades', methods=['GET'])
@jwt_required()
def get_grades(student_id):
    student = Student.query.get_or_404(student_id)
    grades = Grade.query.filter_by(student_id=student.id).all()
    return jsonify([grade.to_dict() for grade in grades])

@students_bp.route('/students/<int:student_id>/fees', methods=['GET'])
@jwt_required()
def get_fees(student_id):
    student = Student.query.get_or_404(student_id)
    fee_balance = FeeBalance.query.filter_by(student_id=student.id).first()
    if fee_balance is None:
        return jsonify({"message": "Fee balance not found"}), 404
    return jsonify(fee_balance.to_dict())

@students_bp.route('/students/<int:student_id>/phase', methods=['GET'])
@jwt_required()
def get_phase(student_id):
    student = Student.query.get_or_404(student_id)
    return jsonify({"current_phase": student.current_phase})

@students_bp.route('/students/<int:student_id>/profile', methods=['PUT'])
@jwt_required()
def update_profile(student_id):
    student = Student.query.get_or_404(student_id)
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

@students_bp.route('/students/<int:student_id>/payments', methods=['POST'])
@jwt_required()
def make_payment(student_id):
    student = Student.query.get_or_404(student_id)
    data = request.get_json()
    
    amount = data.get('amount')
    transaction_id = data.get('transaction_id')
    
    if amount <= 0:
        return jsonify({"message": "Amount must be greater than zero"}), 400
    
    fee_balance = FeeBalance.query.filter_by(student_id=student.id).first()
    if fee_balance is None:
        return jsonify({"message": "Fee balance not found"}), 404
    
    # Calculate new total amount paid and new amount due
    new_amount_paid = fee_balance.amount_paid + amount
    new_amount_due = fee_balance.amount_due - amount
    
    # Check if the new total amount paid exceeds the maximum limit
    max_limit = 200000
    if new_amount_paid > max_limit:
        return jsonify({"message": f"Payment exceeds the maximum limit of {max_limit}"}), 400
    
    # Ensure that the new amount due is not negative
    if new_amount_due < 0:
        return jsonify({"message": "Payment amount exceeds the amount due"}), 400
    
    # Update fee balance and add payment record
    fee_balance.amount_paid = new_amount_paid
    fee_balance.amount_due = new_amount_due
    db.session.add(Payment(student_id=student.id, amount=amount, transaction_id=transaction_id, payment_date=datetime.utcnow()))
    db.session.commit()
    
    return jsonify(fee_balance.to_dict())

@students_bp.route('/students/<int:student_id>/payments/<int:payment_id>', methods=['DELETE'])
@jwt_required()
def delete_payment(student_id, payment_id):
    student = Student.query.get_or_404(student_id)
    payment = Payment.query.filter_by(id=payment_id, student_id=student.id).first_or_404()
    
    fee_balance = FeeBalance.query.filter_by(student_id=student.id).first()
    if fee_balance is None:
        return jsonify({"message": "Fee balance not found"}), 404
    
    # Remove the payment from the database
    db.session.delete(payment)
    
    # Adjust the fee balance
    fee_balance.amount_paid -= payment.amount
    db.session.commit()
    
    return jsonify({"message": "Payment deleted successfully"})
