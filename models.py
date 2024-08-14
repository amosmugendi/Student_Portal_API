from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
from sqlalchemy import event


db = SQLAlchemy()

class User(db.Model, SerializerMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = db.relationship('Student', back_populates='user', uselist=False, cascade="all, delete-orphan", passive_deletes=True)
    admin = db.relationship('Admin', back_populates='user', uselist=False, cascade="all, delete-orphan", passive_deletes=True)

    def __init__(self, username, email, password_hash, role):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class Student(db.Model, SerializerMixin):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    current_phase = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='student')
    course = db.relationship('Course', back_populates='students')
    grades = db.relationship('Grade', back_populates='student', cascade="all, delete-orphan", passive_deletes=True)
    fee_balance = db.relationship('FeeBalance', back_populates='student', uselist=False, cascade="all, delete-orphan", passive_deletes=True)
    payments = db.relationship('Payment', back_populates='student', lazy='dynamic', cascade="all, delete-orphan", passive_deletes=True)

    def __init__(self, user_id, first_name, last_name, date_of_birth, course_id, current_phase):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.course_id = course_id
        self.current_phase = current_phase

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "date_of_birth": self.date_of_birth.isoformat(),
            "course_name": self.course.name if self.course else None,
            "current_phase": self.current_phase,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "email": self.user.email if self.user else None,
            "fee_balance": self.fee_balance.to_dict() if self.fee_balance else None
        }

class Admin(db.Model, SerializerMixin):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='admin')

    def __init__(self, user_id, first_name, last_name):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class Course(db.Model, SerializerMixin):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    fee = db.Column(db.Float, nullable=False)
    duration = db.Column(db.String, nullable=False)
    students = db.relationship('Student', back_populates='course', cascade="all, delete-orphan", passive_deletes=True)
    phases = db.relationship('CourseUnit', back_populates='course', cascade="all, delete-orphan", passive_deletes=True)

    def __init__(self, name, fee, duration):
        self.name = name
        self.fee = fee
        self.duration = duration

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "fee": self.fee,
            "duration": self.duration
        }

class Unit(db.Model, SerializerMixin):
    __tablename__ = 'unit'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    courses = db.relationship('CourseUnit', back_populates='unit', cascade="all, delete-orphan", passive_deletes=True)

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }

class CourseUnit(db.Model, SerializerMixin):
    __tablename__ = 'course_unit'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    phase = db.Column(db.String, nullable=False)

    course = db.relationship('Course', back_populates='phases')
    unit = db.relationship('Unit', back_populates='courses')

    def __init__(self, course_id, unit_id, phase):
        self.course_id = course_id
        self.unit_id = unit_id
        self.phase = phase

    def to_dict(self):
        return {
            "id": self.id,
            "course_id": self.course_id,
            "unit_id": self.unit_id,
            "phase": self.phase
        }

class Grade(db.Model, SerializerMixin):
    __tablename__ = 'grade'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    course_unit_id = db.Column(db.Integer, db.ForeignKey('course_unit.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    grade = db.Column(db.String, nullable=False)
    phase = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = db.relationship('Student', back_populates='grades')
    course_unit = db.relationship('CourseUnit')

    def __init__(self, student_id, course_unit_id, grade, phase):
        self.student_id = student_id
        self.course_unit_id = course_unit_id
        self.grade = grade
        self.phase = phase

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_unit_id': self.course_unit_id,
            'course_name': self.course_unit.course.name if self.course_unit and self.course_unit.course else 'N/A',
            'grade': self.grade,
            'phase': self.phase
        }

class FeeBalance(db.Model, SerializerMixin):
    __tablename__ = 'fee_balance'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    amount_due = db.Column(db.Float, nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)  # Add this line
    due_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = db.relationship('Student', back_populates='fee_balance')

    def __init__(self, student_id, amount_due, amount_paid, due_date):  # Add amount_paid here
        self.student_id = student_id
        self.amount_due = amount_due
        self.amount_paid = amount_paid  # Initialize it here
        self.due_date = due_date

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "amount_due": self.amount_due,
            "amount_paid": self.amount_paid,  # Include it in the dictionary
            "due_date": self.due_date.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class Payment(db.Model):
    __tablename__ = 'payment'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = db.relationship('Student', back_populates='payments')
    transaction = db.relationship('Transaction', back_populates='payment', uselist=False)  # Add back_populates here

    def __init__(self, student_id, amount, payment_date=None, description=None):
        self.student_id = student_id
        self.amount = amount
        self.payment_date = payment_date or datetime.utcnow()
        self.description = description

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "amount": self.amount,
            "payment_date": self.payment_date.isoformat(),
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class Transaction(db.Model):
    __tablename__ = 'transaction'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    trans_for = db.Column(db.String, nullable=True)  # What the transaction was for
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    trans_date = db.Column(db.DateTime, nullable=False)
    user_description = db.Column(db.String, nullable=True)
    mpesa_receipt_number = db.Column(db.String, nullable=True, unique=True)  # M-Pesa receipt number
    payer_names = db.Column(db.String, nullable=True)  # Payer's names from M-Pesa
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id', ondelete="SET NULL"))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)  # New user_id column
    unique_identifier = db.Column(db.String, nullable=True, unique=True)  # Unique identifier for the transaction

    # Relationships
    payment = db.relationship('Payment', back_populates='transaction')
    user = db.relationship('User')  # Relationship with the User model

    def __init__(self, status, phone, trans_for, amount, trans_date, mpesa_receipt_number, payer_names, user_id, unique_identifier, user_description=None):
        self.status = status
        self.phone = phone
        self.trans_for = trans_for
        self.amount = amount
        self.trans_date = trans_date
        self.mpesa_receipt_number = mpesa_receipt_number
        self.payer_names = payer_names
        self.user_id = user_id
        self.unique_identifier = unique_identifier
        self.user_description = user_description

    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "phone": self.phone,
            "trans_for": self.trans_for,
            "amount": float(self.amount),  # Convert from decimal to float for serialization
            "trans_date": self.trans_date.isoformat(),
            "user_description": self.user_description,
            "mpesa_receipt_number": self.mpesa_receipt_number,
            "payer_names": self.payer_names,
            "user_id": self.user_id,  # Include user_id in the dictionary
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "unique_identifier": self.unique_identifier
        }
        
        
# Event Listener to Update FeeBalance after a Payment
@event.listens_for(Payment, 'after_insert')
def update_fee_balance(mapper, connection, target):
    # Fetch the student's fee balance record
    fee_balance = connection.execute(
        db.select([FeeBalance]).where(FeeBalance.student_id == target.student_id)
    ).fetchone()

    # Calculate the new amount_paid
    if fee_balance:
        new_amount_paid = fee_balance.amount_paid + target.amount

        # Update the FeeBalance record
        connection.execute(
            db.update(FeeBalance)
            .where(FeeBalance.id == fee_balance.id)
            .values(amount_paid=new_amount_paid, updated_at=datetime.utcnow())
        )