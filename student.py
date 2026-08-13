from flask import Blueprint, render_template, redirect, request,url_for, flash
from flask_login import login_user, login_required, current_user
from models import db, Student, Warden, Security, Staff, HOD, Admin, Letter, DetailedPass 


student_bp = Blueprint('student',__name__)



# Student Manage

@student_bp.route('/student_login',methods=['POST','GET'])
def student_login() :
    if request.method == 'POST' :
        student = Student.query.filter_by(register=request.form.get('register')).first()
        if student and student.dob == request.form.get('dob') :
            login_user(student)
            return redirect(url_for('student.student_page',id=student.id))
    return render_template('student_login.html')


@student_bp.route('/student_page/<int:id>')
@login_required
def student_page(id) :
    if current_user.id != id:
        return render_template('error_page.html')
    student = Student.query.get_or_404(id)
    # Fetch letters to display on the dashboard
    letters = Letter.query.filter_by(student_id=id).order_by(Letter.id.desc()).all()
    return render_template('student_page.html', student=student,letters=letters)

@student_bp.route('/student_profile/<int:student_id>')
def student_profile(student_id) :
    student = Student.query.get_or_404(student_id)
    return render_template('student_profile.html',student=student)

@student_bp.route('/add_student',methods=['GET','POST'])
def add_student() :
    if request.method == 'POST':
        # Account & Personal Info
        register = request.form.get('register')
        dob = request.form.get('dob')
        name = request.form.get('name')
        
        # Academic & Location Info
        department = request.form.get('department')
        year = request.form.get('year')
        college = request.form.get('college')
        room_no = request.form.get('room_no')
        
        # Contact Numbers (Converted to integers where necessary)
        # Using .get() ensures it doesn't crash if a field is empty
        student_no = request.form.get('student_no')
        father_no = request.form.get('father_no')
        mother_no = request.form.get('mother_no')
        guardient_no = request.form.get('guardient_no')

        # Create the new student object with all fields
        new_student = Student(
            register=register, 
            dob=dob, 
            name=name,
            department=department,
            year=year,
            college=college,
            room_no=room_no,
            student_no=student_no,
            father_no=father_no,
            mother_no=mother_no,
            guardient_no=guardient_no
        )

        # Add to database and commit
        try:
            db.session.add(new_student)
            db.session.commit()
            return redirect(url_for('home'))
            # Redirect or flash success message here
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            # Handle error (e.g., duplicate username)
    return render_template('add_student.html')

@student_bp.route('/students', methods=['GET'])
def view_students():
    # Fetch all students out of your model database
    students = Student.query.order_by(Student.register.asc()).all()
    return render_template('students.html', students=students)

@student_bp.route('/student/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        # Modify the object record structural parameters 
        student.register = request.form.get('register')
        student.name = request.form.get('name')
        student.dob = request.form.get('dob')
        student.department = request.form.get('department')
        student.year = request.form.get('year')
        student.college = request.form.get('college')
        student.room_no = request.form.get('room_no')
        student.student_no = request.form.get('student_no')
        student.father_no = request.form.get('father_no')
        student.mother_no = request.form.get('mother_no')
        student.guardient_no = request.form.get('guardient_no')
        
        db.session.commit()
        flash('Student file data modified successfully.')
        return redirect(url_for('student.view_students'))
        
    return render_template('edit_student.html', student=student)

@student_bp.route('/student/delete/<int:id>', methods=['GET','POST'])
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('student.view_students'))
