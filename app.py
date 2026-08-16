from flask import Flask, render_template, redirect, session, request,url_for, flash, jsonify
from flask_login import LoginManager, login_manager,  login_user, login_required, current_user, logout_user
import json
from datetime import date, datetime
from zoneinfo import ZoneInfo
from models import db, User, Student, Warden, Security, Staff, HOD, Admin, Letter, DetailedPass 
from config import Config
from bulk_import import bulk_import_file
from student import student_bp
from security import security_bp
from hod import hod_bp
from warden import warden_bp
from staff import staff_bp
from admin import admin_bp
from flask_migrate import Migrate

hi purushothaman

# Fetch the exact time specifically for India
local_time = datetime.now(ZoneInfo("Asia/Kolkata"))

app  = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
app.register_blueprint(bulk_import_file)
app.register_blueprint(student_bp)
app.register_blueprint(security_bp)
app.register_blueprint(hod_bp)
app.register_blueprint(warden_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(admin_bp)


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


# Logout Process
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))
    
    
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

