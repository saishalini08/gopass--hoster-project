from flask import Blueprint, render_template, redirect, session, request,url_for, flash, jsonify
from flask_login import LoginManager, login_manager,  login_user, login_required, current_user, logout_user
from models import db, User, Student, Warden, Security, Staff, HOD, Admin, Letter, DetailedPass 
from bulk_import import bulk_import_file
from student import student_bp
from security import security_bp
from hod import hod_bp
from warden import warden_bp

staff_bp = Blueprint('staff',__name__)

#Staff Page
@staff_bp.route('/staff_login',methods=['GET','POST'])
def staff_login() :
    if request.method == 'POST':
        staff = Staff.query.filter_by(username=request.form.get('username')).first()
        if staff and staff.password == request.form.get('password'):
            login_user(staff)
            return redirect(url_for('staff.staff_page',id=staff.id))
    return render_template('staff/staff_login.html')

@staff_bp.route('/staff_page/<int:id>',methods=['GET','POST'])
@login_required
def staff_page(id) :
    if current_user.id != id:
        return render_template('error_page.html')
    staff = Staff.query.get_or_404(id)
    letters = Letter.query.filter_by(nameSelection=staff.name).all()
    return render_template('staff/staff_page.html',staff=staff,letters=letters)

@staff_bp.route('/view_staff',methods=['GET','POST'])
def view_staff() :
    staff = Staff.query.all()
    return render_template('staff/staff.html',staff=staff)

@staff_bp.route('/staff/delete/<int:id>', methods=['GET','POST'])
def delete_staff(id):
    staff = Staff.query.get_or_404(id)
    db.session.delete(staff)
    db.session.commit()
    return redirect(url_for('staff.view_staff')) 

#Approve Letter
@staff_bp.route('/staff_approval_letter/<int:id>', methods=['POST', 'GET'])
@login_required
def staff_approval_letter(id):
    letter = Letter.query.get_or_404(id)
    try:
        # Update the status
        letter.status = 'Pending HOD'
        db.session.commit()
        
        flash(f"Letter from {letter.student_name} has been approved.", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while updating the status.", "danger")

    # Redirect back to the warden's dashboard
    return redirect(url_for('staff.staff_page', id=current_user.id))

@staff_bp.route('/staff_reject_letter/<int:id>', methods=['POST', 'GET'])
@login_required
def staff_reject_letter(id):
    letter = Letter.query.get_or_404(id)
    try:
        # Update the status
        letter.status = 'Rejected Staff'
        db.session.commit()
        
        flash(f"Letter from {letter.student_name} has been rejected.", "warning")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while updating the status.", "danger")

    # Redirect back to the warden's dashboard
    return redirect(url_for('staff.staff_page', id=current_user.id))

