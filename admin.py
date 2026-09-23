from flask import Blueprint, render_template, redirect, session, request,url_for, flash, jsonify
from flask_login import LoginManager, login_manager,  login_user, login_required, current_user, logout_user
from models import db, User, Student, Warden, Security, Staff, HOD, Admin, Letter, DetailedPass 

admin_bp = Blueprint('admin',__name__)

#Admin Page
@admin_bp.route('/admin_login',methods=['GET','POST'])
def admin_login() :
    if request.method == 'POST':
        admin = Admin.query.filter_by(username=request.form.get('username')).first()
        if admin and admin.password == request.form.get('password'):
            login_user(admin)
            return redirect(url_for('admin.admin_page', id=admin.id))
    return render_template('admin/admin_login.html')

@admin_bp.route('/admin_page/<int:id>',methods=['GET','POST'])
@login_required
def admin_page(id) :
    if current_user.id != id:
        return render_template('error_page.html')
    admin = Admin.query.get_or_404(id)
    return render_template('admin/admin_page.html', admin=admin)



@admin_bp.route('/add_warden',methods=['GET','POST'])
def add_warden() :
    if request.method == 'POST' :
        new_warden = Warden(
            username = request.form.get('username'),
            password = request.form.get('password'),
            name = request.form.get('name')
        )
        db.session.add(new_warden)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('warden/add_warden.html')


@admin_bp.route('/add_student',methods=['GET','POST'])
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
    return render_template('student/add_student.html')