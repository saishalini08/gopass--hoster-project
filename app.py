from flask import Flask, render_template, redirect, session, request,url_for, flash, jsonify
from flask_login import LoginManager, login_manager,  login_user, login_required, current_user, logout_user
import json
from datetime import date, datetime
import qrcode
import io
import base64
import pandas as pd
import re
from zoneinfo import ZoneInfo
from models import db, User, Student, Warden, Security, Staff, HOD, Admin, Letter, DetailedPass 
from config import Config
from bulk_import import bulk_import_file
from student import student_bp
from security import security_bp
from hod import hod_bp
from flask_migrate import Migrate

# Fetch the exact time specifically for India
local_time = datetime.now(ZoneInfo("Asia/Kolkata"))

app  = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
app.register_blueprint(bulk_import_file)
app.register_blueprint(student_bp)
app.register_blueprint(security_bp)
app.register_blueprint(hod_bp)


login_manager = LoginManager(app)
login_manager.login_view = 'home'


#Migrate Procedure
migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    # Flask-Login sessions store IDs as strings, so we convert to int
    uid = int(user_id)
    
    user = User.query.get(uid)
    if user:
        return user
    
    student = Student.query.get(uid)
    if student:
        return student
    
    warden = Warden.query.get(uid)
    if warden :
        return warden
    
    staff = Staff.query.get(uid)
    if staff :
        return staff
    
    hod = HOD.query.get(uid)
    if hod :
        return hod
        
    admin = Admin.query.get(uid)
    if admin :
        return admin
        
    return None
        
@app.route('/')
def home() :
    logout_user()
    return render_template('welcome.html')





#Approve Letter
@app.route('/staff_approval_letter/<int:id>', methods=['POST', 'GET'])
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
    return redirect(url_for('staff_page', id=current_user.id))

@app.route('/warden_approval_letter/<int:id>', methods=['POST', 'GET'])
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
    return redirect(url_for('warden_page', id=current_user.id))


@app.route('/staff_reject_letter/<int:id>', methods=['POST', 'GET'])
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
    return redirect(url_for('staff_page', id=current_user.id))



# Logout Process
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))
    
#Staff Page
@app.route('/staff_login',methods=['GET','POST'])
def staff_login() :
    if request.method == 'POST':
        staff = Staff.query.filter_by(username=request.form.get('username')).first()
        if staff and staff.password == request.form.get('password'):
            login_user(staff)
            return redirect(url_for('staff_page',id=staff.id))
    return render_template('staff_login.html')

@app.route('/staff_page/<int:id>',methods=['GET','POST'])
@login_required
def staff_page(id) :
    if current_user.id != id:
        return render_template('error_page.html')
    staff = Staff.query.get_or_404(id)
    letters = Letter.query.filter_by(nameSelection=staff.name).all()
    return render_template('staff_page.html',staff=staff,letters=letters)




#Admin Page
@app.route('/admin_login',methods=['GET','POST'])
def admin_login() :
    if request.method == 'POST':
        admin = Admin.query.filter_by(username=request.form.get('username')).first()
        if admin and admin.password == request.form.get('password'):
            login_user(admin)
            return redirect(url_for('admin_page', id=admin.id))
    return render_template('admin_login.html')

@app.route('/admin_page/<int:id>',methods=['GET','POST'])
@login_required
def admin_page(id) :
    if current_user.id != id:
        return render_template('error_page.html')
    admin = Admin.query.get_or_404(id)
    return render_template('admin_page.html', admin=admin)

    
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='user').first():
        db.session.add(User(username='user', password='user123'))
        db.session.commit()
    if not Admin.query.filter_by(username='Adhi').first() :
        db.session.add(Admin(username='Adhi', password='Adhi123',name='Adhi Admin'))
        db.session.commit()


if __name__ == '__main__' :
    app.run(debug=True)

