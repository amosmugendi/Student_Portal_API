from app import app
from models import db, User, Student, Admin, Course, Unit, CourseUnit, Grade, FeeBalance, Payment
from datetime import datetime
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def seed_data():
    with app.app_context():
        # Drop all tables and create them again
        db.drop_all()
        db.create_all()

        # Create Courses
        course1 = Course(name='Computer Science', fee=150000, duration=6)
        course2 = Course(name='Information Technology', fee=140000, duration=4)
        db.session.add_all([course1, course2])
        db.session.commit()

        # Create Units
        unit1 = Unit(name='Data Structures', description='Fundamentals of data organization')
        unit2 = Unit(name='Algorithms', description='Design and analysis of algorithms')
        unit3 = Unit(name='Database Systems', description='Introduction to database systems')
        db.session.add_all([unit1, unit2, unit3])
        db.session.commit()

        # Create CourseUnits
        course_unit1 = CourseUnit(course_id=course1.id, unit_id=unit1.id, phase='Phase 1')
        course_unit2 = CourseUnit(course_id=course1.id, unit_id=unit2.id, phase='Phase 1')
        course_unit3 = CourseUnit(course_id=course2.id, unit_id=unit3.id, phase='Phase 1')
        db.session.add_all([course_unit1, course_unit2, course_unit3])
        db.session.commit()

        # Create Users
        hashed_password1 = bcrypt.generate_password_hash('password123').decode('utf-8')
        hashed_password2 = bcrypt.generate_password_hash('adminpassword').decode('utf-8')
        user1 = User(username='john_doe', email='john@example.com', password_hash=hashed_password1, role='student')
        user2 = User(username='admin_user', email='admin@example.com', password_hash=hashed_password2, role='admin')
        db.session.add_all([user1, user2])
        db.session.commit()

        # Create Students
        student1 = Student(user_id=user1.id, first_name='John', last_name='Doe', date_of_birth=datetime.strptime('2000-01-01', '%Y-%m-%d').date(), course_id=course1.id, current_phase='Phase 1')
        db.session.add(student1)
        db.session.commit()

        # Create Admins
        admin1 = Admin(user_id=user2.id, first_name='Admin', last_name='User')
        db.session.add(admin1)
        db.session.commit()

        # Create FeeBalances
        fee_balance1 = FeeBalance(student_id=student1.id, amount_due=150000, amount_paid=75000, due_date=datetime.strptime('2024-12-31', '%Y-%m-%d').date())
        db.session.add(fee_balance1)
        db.session.commit()

        # Create Grades
        grade1 = Grade(student_id=student1.id, course_unit_id=course_unit1.id, grade='A', phase='Phase 1')
        db.session.add(grade1)
        db.session.commit()

        # Create Payments
        payment1 = Payment(student_id=student1.id, amount=75000, payment_date=datetime.utcnow(), transaction_id='txn_001')
        db.session.add(payment1)
        db.session.commit()

        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_data()