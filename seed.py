from app import app
from models import db, User, Student, Admin, Course, Unit, CourseUnit, Grade, FeeBalance, Payment
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
import random

bcrypt = Bcrypt()

def seed_data():
    with app.app_context():
        # Drop all tables and create them again
        db.drop_all()
        db.create_all()

        # Create Courses
        courses = [
            Course(name='Data Science', fee=120000, duration='6 months'),
            Course(name='Project Design', fee=110000, duration='5 months'),
            Course(name='Cybersecurity', fee=130000, duration='6 months'),
            Course(name='Data Analytics', fee=115000, duration='5 months'),
            Course(name='Mobile App Development', fee=125000, duration='6 months'),
            Course(name='CompTIA Security+ Bootcamp', fee=140000, duration='4 months'),
            Course(name='Software Engineering', fee=150000, duration='8 months'),
        ]
        db.session.add_all(courses)
        db.session.commit()

        # Create Units
        units = [
            Unit(name='Introduction to Data Science', description='Overview of data science principles, methodologies, and tools used for extracting insights from data and making informed decisions.'),
            Unit(name='Data Analysis with Python', description='Techniques for analyzing data using Python libraries like Pandas and NumPy, including data manipulation, cleaning, and exploration.'),
            Unit(name='Machine Learning', description='Study of algorithms that enable computers to learn from data and make predictions or decisions without explicit programming.'),
            Unit(name='Data Visualization', description='Methods and tools for creating graphical representations of data to identify trends, patterns, and insights effectively.'),
            Unit(name='Big Data Technologies', description='Exploration of technologies and frameworks for handling and processing large-scale data, including Hadoop, Spark, and distributed computing.'),
            Unit(name='Introduction to Project Management', description='Fundamentals of managing projects, including project initiation, planning, execution, monitoring, and closure for successful project delivery.'),
            Unit(name='Project Planning and Scheduling', description='Techniques for planning project activities, setting timelines, allocating resources, and scheduling tasks to meet project objectives.'),
            Unit(name='Risk Management', description='Identification, analysis, and mitigation of risks that could impact project success, including strategies for managing and minimizing risks.'),
            Unit(name='Budgeting and Cost Management', description='Methods for estimating project costs, developing budgets, and controlling expenses to ensure financial resources are used efficiently.'),
            Unit(name='Project Evaluation and Closure', description='Processes for evaluating project performance, assessing outcomes, and formally closing the project, including post-project reviews and documentation.'),
            Unit(name='Introduction to Cybersecurity', description='Basics of cybersecurity, including principles of protecting systems, networks, and data from cyber threats and attacks.'),
            Unit(name='Network Security', description='Techniques and practices for safeguarding network infrastructure, including firewalls, intrusion detection systems, and network encryption.'),
            Unit(name='Threat and Vulnerability Management', description='Identification, assessment, and management of security threats and vulnerabilities to prevent potential exploitation and breaches.'),
            Unit(name='Security Operations', description='Management of security operations, including monitoring, incident response, and maintaining the security posture of an organization.'),
            Unit(name='Ethical Hacking and Penetration Testing', description='Techniques for testing and evaluating system security by simulating attacks to identify and address vulnerabilities.'),
            Unit(name='Introduction to Data Analytics', description='Overview of data analytics processes, including data collection, analysis, and interpretation to support decision-making and business strategies.'),
            Unit(name='Statistical Analysis', description='Application of statistical methods to analyze data, including hypothesis testing, regression analysis, and probability distributions.'),
            Unit(name='Data Cleaning and Preparation', description='Techniques for cleaning, transforming, and preparing raw data for analysis to ensure accuracy and reliability in results.'),
            Unit(name='Data Visualization Techniques', description='Methods for creating visual representations of data, such as charts and graphs, to effectively communicate findings and insights.'),
            Unit(name='Predictive Analytics', description='Use of statistical models and machine learning techniques to predict future trends and behaviors based on historical data.'),
            Unit(name='Introduction to Mobile Development', description='Fundamentals of developing mobile applications, including platform differences, development environments, and key concepts in mobile design.'),
            Unit(name='Android Development Basics', description='Basic principles and tools for developing Android applications, including Java/Kotlin programming, Android Studio, and app lifecycle management.'),
            Unit(name='iOS Development Basics', description='Fundamentals of developing iOS applications, including Swift programming, Xcode IDE, and the iOS app lifecycle and design principles.'),
            Unit(name='Mobile User Interface Design', description='Best practices for designing intuitive and user-friendly interfaces for mobile applications, focusing on user experience and usability.'),
            Unit(name='Mobile App Testing and Deployment', description='Techniques for testing mobile applications for functionality, performance, and usability, and deploying them to app stores.'),
            Unit(name='Security Fundamentals', description='Basic concepts and principles of cybersecurity, including threats, vulnerabilities, and security controls necessary to protect information systems.'),
            Unit(name='Network Security', description='Techniques and practices for securing network infrastructure, including firewalls, VPNs, and network segmentation to prevent unauthorized access.'),
            Unit(name='Threats and Vulnerabilities', description='Identification and analysis of potential security threats and vulnerabilities in systems, including methods to address and mitigate them.'),
            Unit(name='Risk Management', description='Processes for assessing and managing risks in cybersecurity, including risk assessment, mitigation strategies, and incident response planning.'),
            Unit(name='Cryptography and Public Key Infrastructure (PKI)', description='Study of encryption methods and PKI systems for securing data, including encryption algorithms, digital certificates, and key management.'),
            Unit(name='Introduction to Software Engineering', description='Overview of software engineering principles, practices, and methodologies for designing, developing, and maintaining software systems.'),
            Unit(name='Software Development Life Cycle (SDLC)', description='Phases of the SDLC, including planning, analysis, design, implementation, testing, and maintenance of software projects.'),
            Unit(name='Requirements Engineering', description='Process of gathering, analyzing, and documenting software requirements to ensure the final product meets user needs and expectations.'),
            Unit(name='Software Design and Architecture', description='Principles and practices for designing software systems, including architectural patterns, design principles, and modularity.'),
            Unit(name='Software Testing and Quality Assurance', description='Techniques for testing software to ensure functionality, reliability, and performance, including various testing methods and quality assurance practices.'),
            Unit(name='Agile Methodologies', description='Frameworks and practices for Agile software development, including Scrum and Kanban, focusing on iterative development and continuous improvement.'),
            Unit(name='Software Project Management', description='Techniques for managing software projects, including project planning, tracking progress, resource management, and team coordination.'),
            Unit(name='Version Control Systems', description='Tools and practices for managing changes to source code, including Git, version branching, merging, and collaboration.'),
            Unit(name='Software Maintenance and Evolution', description='Processes for maintaining and evolving software systems, including bug fixes, updates, and adapting to changing requirements.'),
            Unit(name='User Experience (UX) Design', description='Principles and practices for designing user-friendly and engaging software interfaces, focusing on user needs, usability, and accessibility.'),
        ]
        db.session.add_all(units)
        db.session.commit()

        # Create CourseUnits
        course_units = []
        for course in courses:
            for unit in units:
                phase = f'Phase {random.randint(1, 5)}'
                course_units.append(CourseUnit(course_id=course.id, unit_id=unit.id, phase=phase))
        db.session.add_all(course_units)
        db.session.commit()

        # Create Users
        students = []
        admins = []
        for i in range(30):
            hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
            username = f'student{i+1}'
            email = f'student{i+1}@example.com'
            user = User(username=username, email=email, password_hash=hashed_password, role='student')
            students.append(user)
        for i in range(10):
            hashed_password = bcrypt.generate_password_hash('adminpassword').decode('utf-8')
            username = f'admin{i+1}'
            email = f'admin{i+1}@example.com'
            user = User(username=username, email=email, password_hash=hashed_password, role='admin')
            admins.append(user)
        db.session.add_all(students + admins)
        db.session.commit()

        # Create Students
        for user in students:
            course = random.choice(courses)
            current_phase = f'Phase {random.randint(1, 5)}'
            
            # Get full name from the list
            full_name = random.choice([
                'James Smith', 'Emily Johnson', 'Michael Brown', 'Sarah Davis', 'John Wilson', 'Jessica Moore', 'Robert Taylor', 'Olivia Anderson', 
                'William Thomas', 'Sophia Martinez', 'David Lee', 'Isabella Clark', 'Richard Lewis', 'Charlotte Hall', 'Joseph Young', 'Amelia King', 
                'Charles Scott', 'Mia Wright', 'Daniel Adams', 'Ella Baker', 'Matthew Nelson', 'Grace Carter', 'Andrew Mitchell', 'Ava Perez', 
                'Thomas Roberts', 'Hannah Turner', 'George Phillips', 'Lily Campbell', 'Paul Evans', 'Zoe Parker', 'Edward Edwards', 'Natalie Collins', 
                'Brian Stewart', 'Lucy Morris', 'Kevin Richardson', 'Chloe Hughes', 'Samuel Green', 'Ruby Sanders', 'Steven Price', 'Lila Bennett'
            ])
            first_name, last_name = full_name.split(' ', 1)
            
            # Generate a random date of birth
            date_of_birth = datetime(2000, 1, 1) + timedelta(days=random.randint(0, 7300))
            
            student = Student(user_id=user.id, first_name=first_name, last_name=last_name, date_of_birth=date_of_birth, course_id=course.id, current_phase=current_phase)
            db.session.add(student)
        db.session.commit()

        # Create Admins
        for user in admins:
            admin = Admin(user_id=user.id, first_name=user.username.split('_')[0].capitalize(), last_name='Admin')
            db.session.add(admin)
        db.session.commit()

        # Create FeeBalances
        for student in Student.query.all():
            fee_balance = FeeBalance(student_id=student.user_id, amount_due=random.randint(10000, 50000), amount_paid=random.randint(5000, 25000), due_date=datetime(2024, 12, 31).date())
            db.session.add(fee_balance)
        db.session.commit()

        # Create Grades
        for student in Student.query.all():
            for course_unit in CourseUnit.query.filter_by(course_id=student.course_id).all():
                grade = Grade(student_id=student.user_id, course_unit_id=course_unit.id, grade=random.choice(['A', 'B', 'C', 'D', 'E']), phase=student.current_phase)
                db.session.add(grade)
        db.session.commit()

        # Create Payments
        for student in Student.query.all():
            for _ in range(2):  # Each student gets 2 payment entries
                payment = Payment(student_id=student.user_id, amount=random.randint(5000, 20000), payment_date=datetime.utcnow(), transaction_id=f'txn_{random.randint(1000, 9999)}', description='Fees')
                db.session.add(payment)
        db.session.commit()

        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_data()