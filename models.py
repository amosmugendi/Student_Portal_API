from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

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

    student = db.relationship('Student', back_populates='user', uselist=False)
    admin = db.relationship('Admin', back_populates='user', uselist=False)

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
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class Student(db.Model, SerializerMixin):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    current_phase = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='student')
    course = db.relationship('Course', back_populates='students')
    grades = db.relationship('Grade', back_populates='student')
    fee_balance = db.relationship('FeeBalance', back_populates='student', uselist=False)
    payments = db.relationship('Payment', back_populates='student', lazy='dynamic')

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
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "email": self.user.email if self.user else None
        }

class Admin(db.Model, SerializerMixin):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
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
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class Course(db.Model, SerializerMixin):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    fee = db.Column(db.Float, nullable=False)
    duration = db.Column(db.String, nullable=False)
    students = db.relationship('Student', back_populates='course')
    phases = db.relationship('CourseUnit', back_populates='course')

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
    courses = db.relationship('CourseUnit', back_populates='unit')

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
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)
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
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_unit_id = db.Column(db.Integer, db.ForeignKey('course_unit.id'), nullable=False)
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
            'course_name': self.course_unit.course.name,
            'grade': self.grade,
            'phase': self.phase
        }

class FeeBalance(db.Model, SerializerMixin):
    __tablename__ = 'fee_balance'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    amount_due = db.Column(db.Float, nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = db.relationship('Student', back_populates='fee_balance')

    def __init__(self, student_id, amount_due, amount_paid, due_date):
        self.student_id = student_id
        self.amount_due = amount_due
        self.amount_paid = amount_paid
        self.due_date = due_date

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "amount_due": self.amount_due,
            "amount_paid": self.amount_paid,
            "due_date": self.due_date.isoformat(),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class Payment(db.Model, SerializerMixin):
    __tablename__ = 'payment'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    transaction_id = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = db.relationship('Student', back_populates='payments')

    def __init__(self, student_id, amount, payment_date, transaction_id):
        self.student_id = student_id
        self.amount = amount
        self.payment_date = payment_date
        self.transaction_id = transaction_id

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "amount": self.amount,
            "payment_date": self.payment_date.isoformat(),
            "transaction_id": self.transaction_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }