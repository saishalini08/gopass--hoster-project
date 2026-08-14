
from flask import Blueprint, render_template, redirect, session, request,url_for, flash, jsonify
from flask_login import LoginManager, login_manager,  login_user, login_required, current_user, logout_user
from models import db, User, Student, Warden, Security, Staff, HOD, Admin, Letter, DetailedPass 

from student import student_bp
from security import security_bp
from hod import hod_bp


warden_bp = Blueprint('warden',__name__)

# Warden Manage
@warden_bp.route('/warden_login',methods=['POST','GET'])
def warden_login() :
    if request.method == 'POST' :
        warden = Warden.query.filter_by(username=request.form.get('username')).first()
        if warden and warden.password == request.form.get('password') :
            login_user(warden)
            return redirect(url_for('warden.warden_page',id=warden.id))
    return render_template('warden/warden_login.html')


@warden_bp.route('/warden_page/<int:id>', methods=['GET', 'POST'])
@login_required
def warden_page(id):
    if current_user.id != id:
        return render_template('error_page.html')
    warden = Warden.query.get_or_404(id)
    letters = Letter.query.filter_by(nameSelection=warden.name).all()
    
    return render_template('warden/warden_page.html', warden=warden, letters=letters)



@warden_bp.route('/warden_approval_letter/<int:id>', methods=['POST', 'GET'])
@login_required
def warden_approval_letter(id):
    letter = Letter.query.get_or_404(id)
    try:
        # Update the status
        letter.status = 'Approved'
        db.session.commit()
        
        flash(f"Letter from {letter.student_name} has been approved.", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while updating the status.", "danger")

    # Redirect back to the warden's dashboard
    return redirect(url_for('warden.warden_page', id=current_user.id))


@warden_bp.route('/approval_letter/<int:id>', methods=['POST', 'GET'])
@login_required
def approval_letter(id):
    letter = Letter.query.get_or_404(id)
    try:
        # Update the status
        letter.status = 'Approved'
        db.session.commit()
        
        flash(f"Letter from {letter.student_name} has been approved.", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while updating the status.", "danger")

    # Redirect back to the warden's dashboard
    return redirect(url_for('warden.warden_page', id=current_user.id))


@warden_bp.route('/warden_page/approval_letters/<int:id>',methods=['GET','POST'])    
def warden_approval_letter_list(id) :
    warden = Warden.query.get_or_404(id)
    letters = Letter.query.all()
    return render_template('warden/approved_letters.html',warden=warden,letters=letters)

#Reject Letter
@warden_bp.route('/reject_letter/<int:id>', methods=['POST', 'GET'])
@login_required
def reject_letter(id):
    letter = Letter.query.get_or_404(id)

    try:
        # Update the status
        letter.status = 'Rejected'
        db.session.commit()
        
        flash(f"Letter from {letter.student_name} has been rejected.", "warning")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while updating the status.", "danger")

    # Redirect back to the warden's dashboard
    return redirect(url_for('warden.warden_page', id=current_user.id))



@warden_bp.route('/warden_reject_letter/<int:id>', methods=['POST', 'GET'])
@login_required
def warden_reject_letter(id):
    letter = Letter.query.get_or_404(id)
    try:
        # Update the status
        letter.status = 'Rejected Warden'
        db.session.commit()
        
        flash(f"Letter from {letter.student_name} has been rejected.", "warning")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while updating the status.", "danger")

    # Redirect back to the warden's dashboard
    return redirect(url_for('warden.warden_page', id=current_user.id))


@warden_bp.route('/warden_page/rejected_letters/<int:id>',methods=['GET','POST'])    
def warden_rejected_letter(id) :
    warden = Warden.query.get_or_404(id)
    letters = Letter.query.all()
    return render_template('warden/rejected_letters.html',warden=warden,letters=letters)

