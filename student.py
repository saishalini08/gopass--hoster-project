from flask import Blueprint, render_template, redirect, request,url_for, flash
from flask_login import login_user, login_required, current_user
from models import db, Student, Warden, Security, Staff, HOD, Admin, Letter, DetailedPass 
from flask_login import  login_user, login_required, current_user, logout_user
from datetime import date, datetime
import qrcode
import io
import base64

student_bp = Blueprint('student',__name__)


# Student Manage

@student_bp.route('/student_login', methods=['POST','GET'])
def student_login() :
    if request.method == 'POST' :
        student = Student.query.filter_by(register=request.form.get('register')).first()
        if student and student.dob == request.form.get('dob') :
            login_user(student)
            return redirect(url_for('student.student_page',id=student.id))
    return render_template('student/student_login.html')


@student_bp.route('/student_page/<int:id>')
@login_required
def student_page(id) :
    if current_user.id != id:
        return render_template('error_page.html')
    student = Student.query.get_or_404(id)
    # Fetch letters to display on the dashboard
    letters = Letter.query.filter_by(student_id=id).order_by(Letter.id.desc()).all()
    return render_template('student/student_page.html', student=student,letters=letters)

@student_bp.route('/student_profile/<int:student_id>')
def student_profile(student_id) :
    student = Student.query.get_or_404(student_id)
    return render_template('student/student_profile.html',student=student)

@student_bp.route('/request_letter/<int:student_id>',methods=['GET','POST'])
@login_required
def request_letter(student_id) :
    student = Student.query.get_or_404(student_id)
    warden =  Warden.query.all()
    # Query all names and organize into a dictionary
    # This matches the 'value' attributes in your HTML <select>
    db_data = {
        "warden": [w.name for w in Warden.query.all()],
        "staff": [st.name for st in Staff.query.all()],
        "HOD" : [h.name for h in HOD.query.all()]
    }
    today_date = date.today().strftime('%Y-%m-%d')
    return render_template('student/request_letter.html',data=db_data, student=student,warden=warden,today=today_date)


@student_bp.route('/students', methods=['GET'])
def view_students():
    # Fetch all students out of your model database
    students = Student.query.order_by(Student.register.asc()).all()
    return render_template('student/students.html', students=students)


# @student_bp.route('/student/student_list')
# def student_list() :
    

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
        
    return render_template('student/edit_student.html', student=student)

@student_bp.route('/student/delete/<int:id>', methods=['GET','POST'])
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('student.view_students'))

    
#Letter Submit
@student_bp.route('/submit_request', methods=['POST'])
def submit_request():
    if request.method == 'POST':
        # Convert HTML datetime-local strings to Python datetime objects
        start_str = request.form.get('parent_start_time')
        end_str = request.form.get('parent_end_time')
        
        # Formatting the time (HTML returns YYYY-MM-DDTHH:MM)
        start_dt = datetime.strptime(start_str, '%Y-%m-%dT%H:%M') if start_str else None
        end_dt = datetime.strptime(end_str, '%Y-%m-%dT%H:%M') if end_str else None
        # 1. First, determine the approval statuses based on the category
        category = request.form.get('category')
        if category == 'staff':
            status = 'Pending Staff'
        elif category == 'HOD':
            status = 'Pending HOD'
        else:
            status = 'Pending Warden'
        # 2. Now, safely instantiate the Letter object
        new_letter = Letter(
            student_name=request.form.get('student_name'),
            student_department=request.form.get('department'),
            student_year=request.form.get('year'),
            student_college=request.form.get('college'),
            category=category,
            nameSelection=request.form.get('nameSelection'),
            letter_content=request.form.get('letter_content'),
            request_date=request.form.get('request_date'),
            parent_name=request.form.get('parent_name'),
            parent_no=request.form.get('parent_no'),
            parent_start_time=start_dt,
            parent_end_time=end_dt,
            request_category=request.form.get('request_category'),
            status=status,
            student_id=current_user.id  # Link to the logged-in student
        )

        db.session.add(new_letter)
        db.session.commit()
        flash("Letter submitted to the warden successfully!", "success")
        return redirect(url_for('student.student_page',id=current_user.id))

@student_bp.route('/qr_code/<int:letter_id>', methods=['GET'])
def qr_code(letter_id):
    # 1. Get the letter data
    letter = Letter.query.get_or_404(letter_id)
    
    # CRITICAL FIX: Encode just the raw string ID instead of complex JSON
    qr_data = str(letter.id) 

    # 3. Generate QR Image with High Error Correction
    qr = qrcode.QRCode(
        version=None, 
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # 4. Save to memory buffer
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    
    # 5. Convert to string for HTML
    qr_base64 = base64.b64encode(buf.getvalue()).decode('ascii')
    
    return render_template('scanner/qr_code.html', qr_code=qr_base64, letter=letter)
