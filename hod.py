from flask import Blueprint, render_template, redirect, session, request,url_for, flash, jsonify
from flask_login import LoginManager, login_manager,  login_user, login_required, current_user, logout_user
from models import db, User, Student, Warden, Security, Staff, HOD, Admin, Letter, DetailedPass 
from config import Config
from bulk_import import bulk_import_file
from student import student_bp
from security import security_bp


hod_bp = Blueprint('hod',__name__)

#HOD Page
@hod_bp.route('/hod_login',methods=['GET','POST'])
def hod_login() :
    if request.method == 'POST':
        hod = HOD.query.filter_by(username=request.form.get('username')).first()
        if hod and hod.password == request.form.get('password'):
            login_user(hod)     
            return redirect(url_for('hod.hod_page',id=hod.id))
    return render_template('hod/hod_login.html')

@hod_bp.route('/hod_page/<int:id>',methods=['GET','POST'])
@login_required
def hod_page(id) :
    if current_user.id != id:
        return render_template('error_page.html')
    hod = HOD.query.get_or_404(id)
    letters = Letter.query.filter_by(student_department=hod.department).all()
    warden = Warden.query.all()
    return render_template('hod/hod_page.html',hod=hod,letters=letters,warden=warden)


@hod_bp.route('/view_hod',methods=['GET','POST'])
def view_hod() :
    hods = HOD.query.all()
    return render_template('hod/hod.html',hods=hods)

@hod_bp.route('/hod/delete/<int:id>', methods=['GET','POST'])
def delete_hod(id):
    hod = HOD.query.get_or_404(id)
    db.session.delete(hod)
    db.session.commit()
    return redirect(url_for('hod.view_hod')) 

@hod_bp.route('/hod_approval_letter/<int:id>', methods=['POST', 'GET'])
@login_required
def hod_approval_letter(id):
    letter = Letter.query.get_or_404(id)
    warden = Warden.query.all()
    try:
        # Update the status
        if request.form.get('nameSelection') :
            letter.nameSelection = request.form.get('nameSelection')
            letter.status = 'Pending Warden'
            db.session.commit()
        
        
        flash(f"Letter from {letter.student_name} has been approved.", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while updating the status.", "danger")

    # Redirect back to the warden's dashboard
    return redirect(url_for('hod.hod_page', id=current_user.id,warden=warden))


@hod_bp.route('/hod_reject_letter/<int:id>', methods=['POST', 'GET'])
@login_required
def hod_reject_letter(id):
    letter = Letter.query.get_or_404(id)
    try:
        # Update the status
        letter.status = 'Rejected HOD'
        db.session.commit()
        
        flash(f"Letter from {letter.student_name} has been rejected.", "warning")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while updating the status.", "danger")

    # Redirect back to the warden's dashboard
    return redirect(url_for('hod.hod_page', id=current_user.id))
