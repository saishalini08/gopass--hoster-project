from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# Stack Holder Details 

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))

class Student(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    register = db.Column(db.String(12), unique=True, nullable=False)
    dob = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100))
    year = db.Column(db.String(2)) 
    college = db.Column(db.String(100))
    room_no = db.Column(db.String(6))
    gender = db.Column(db.String(10),default="Male")
    accommodation_type = db.Column(db.String(20),default="Hostel")

    # Changed from Integer to String(15) to protect leading zeros 
    # and avoid mathematical overflow errors
    student_no = db.Column(db.String(15),nullable=False)
    father_no = db.Column(db.String(15),nullable=True)
    mother_no = db.Column(db.String(15),nullable=True)
    guardient_no = db.Column(db.String(15),nullable=True)
    status = db.Column(db.String(20),default="In Campus")

    def __repr__(self):
        return f'<Student {self.register}>'
    
class Warden(UserMixin, db.Model) :
    id = db.Column(db.Integer,primary_key=True)
    username =  db.Column(db.String(50),unique=True)
    password = db.Column(db.String(50))
    name = db.Column(db.String(50))

class Security(UserMixin, db.Model) :
    id = db.Column(db.Integer,primary_key=True)
    username =  db.Column(db.String(50),unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(50)) 
    
class Staff(UserMixin, db.Model) :
    id = db.Column(db.Integer,primary_key=True)
    username =  db.Column(db.String(50),unique=True)
    name = db.Column(db.String(50))
    department = db.Column(db.String(50)) #AI&DS, IT, CSE, ECE, AI&ML, EEE, MECH, CY 
    password = db.Column(db.String(50)) 

class HOD(UserMixin, db.Model) :
    id = db.Column(db.Integer,primary_key=True)
    username =  db.Column(db.String(50),unique=True)
    name = db.Column(db.String(50))
    department = db.Column(db.String(50)) #AI&DS, IT, CSE, ECE, AI&ML, EEE, MECH, CY 
    password = db.Column(db.String(50)) 

class Admin(UserMixin, db.Model) :
    id = db.Column(db.Integer,primary_key=True)
    username =  db.Column(db.String(50),unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(50)) 

#Letter Processing
class Letter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Student Info (Snapshot at time of request)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    student_name = db.Column(db.String(50))
    student_department = db.Column(db.String(60))
    student_year = db.Column(db.String(10))
    student_college = db.Column(db.String(100))
    
    # Request Details
    category = db.Column(db.String(50))  # e.g., 'Staff, HOD, Warden'
    nameSelection = db.Column(db.String(50))
    letter_content = db.Column(db.Text)   # The main body text
    request_category = db.Column(db.String(50))
    request_date = db.Column(db.String(20)) # The date string from the form
    out_date_time = db.Column(db.String(20))
    in_date_time = db.Column(db.String(20))
    
    # Adds a relationship directly to the Student model
    student = db.relationship('Student', backref='letters')
    # Parent/Guardian Details
    parent_name = db.Column(db.String(100))
    parent_no = db.Column(db.String(100))
    parent_start_time = db.Column(db.DateTime)
    parent_end_time = db.Column(db.DateTime)
    
    # Status & Routing
    status = db.Column(db.String(20), default='active') # Pending, Approved, Rejected
    # warden_name = db.Column(db.String(50)) # The ID of the warden selected in the form
    
    # Relationship Link
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Letter {self.id} from {self.student_name}>'
    

#Detailed Pass
class DetailedPass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    letter_id = db.Column(db.String(50))
    student_name = db.Column(db.String(150))
    dept = db.Column(db.String(100))
    year = db.Column(db.String(20))
    scanned_at = db.Column(db.DateTime, default=datetime.utcnow)
