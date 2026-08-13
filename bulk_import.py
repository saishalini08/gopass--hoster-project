from flask import Blueprint, render_template, redirect,  request,url_for, flash 
from flask_login import current_user
import pandas as pd
from models import db, Student, Warden, Staff, HOD

bulk_import_file = Blueprint('file_upload',__name__)


# ==============================
# Bulk Upload Route 
# ==============================
# --- Helper for File Validation ---
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# --- Route for File Upload & Processing ---
@bulk_import_file.route('/upload_students', methods=['GET', 'POST'])
def upload_students():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part in the request.', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected. Please choose a file.', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            
            try:
                # Force specific columns to be read as strings to preserve leading zeros
                string_columns = ['register', 'year', 'room_no', 'student_no', 'father_no', 'mother_no', 'guardient_no']
                converters = {col: str for col in string_columns}
                
                # Parse based on file type using pandas
                if file_ext == 'csv':
                    df = pd.read_csv(file, converters=converters)
                else:
                    df = pd.read_excel(file, converters=converters)
                
                df.columns = df.columns.str.strip()
                df = df.where(pd.notnull(df), None)
                
                students_to_add = []
                duplicate_errors = []
                
                for index, row in df.iterrows():
                    register_val = str(row.get('register', '')).strip() if row.get('register') else None
                    name_val = str(row.get('name', '')).strip() if row.get('name') else None
                    dob_val = str(row.get('dob')).strip().split(' ')[0] if row.get('dob') else None
                    
                    if not register_val or not name_val or not dob_val:
                        continue
                        
                    existing = Student.query.filter_by(register=register_val).first()
                    if existing:
                        duplicate_errors.append(f"Row {index + 2}: Register '{register_val}' already exists. Skipped.")
                        continue
                    
                    student = Student(
                        register=register_val,
                        dob=dob_val,
                        name=name_val,
                        department=row.get('department'),
                        year=row.get('year'),
                        college=row.get('college'),
                        room_no=row.get('room_no'),
                        student_no=row.get('student_no'),
                        father_no=row.get('father_no'),
                        mother_no=row.get('mother_no'),
                        guardient_no=row.get('guardient_no')
                    )
                    students_to_add.append(student)
                
                if students_to_add:
                    db.session.bulk_save_objects(students_to_add)
                    db.session.commit()
                    flash(f'Successfully imported {len(students_to_add)} new student records!', 'success')
                
                if duplicate_errors:
                    for err in duplicate_errors:
                        flash(err, 'warning')
                 
                return redirect(url_for('admin_page', id=current_user.id))
                
            except Exception as e:
                db.session.rollback()
                flash(f"Error parsing file: {str(e)}", 'danger')
                return redirect(request.url)
                
        else:
            flash('Invalid format! Please use a valid .csv, .xlsx, or .xls file.', 'danger')
            return redirect(request.url)
            
    return render_template('student_bulk_import.html')


# --- Route for HOD File Upload & Processing ---
@bulk_import_file.route('/upload_hod', methods=['GET', 'POST'])
def upload_hod():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part in the request.', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected. Please choose a file.', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            
            try:
                # Force username and password to string to keep format intact (e.g. leading zeros)
                string_columns = ['username', 'password']
                converters = {col: str for col in string_columns}
                
                # Parse file
                if file_ext == 'csv':
                    df = pd.read_csv(file, converters=converters)
                else:
                    df = pd.read_excel(file, converters=converters)
                
                # Clean up whitespaces from headers
                df.columns = df.columns.str.strip()
                df = df.where(pd.notnull(df), None)
                
                hods_to_add = []
                duplicate_errors = []
                
                # Iterate rows
                for index, row in df.iterrows():
                    username_val = str(row.get('username', '')).strip() if row.get('username') else None
                    name_val = str(row.get('name', '')).strip() if row.get('name') else None
                    dept_val = str(row.get('department', '')).strip() if row.get('department') else None
                    password_val = str(row.get('password', '')).strip() if row.get('password') else None
                    
                    # Validate required fields
                    if not username_val or not name_val or not password_val:
                        continue # Skip empty or invalid rows
                        
                    # Check for existing username duplicates
                    existing = HOD.query.filter_by(username=username_val).first()
                    if existing:
                        duplicate_errors.append(f"Row {index + 2}: Username '{username_val}' already exists. Skipped.")
                        continue
                    
                    hod = HOD(
                        username=username_val,
                        name=name_val,
                        department=dept_val,
                        password=password_val # Note: Consider using generate_password_hash in real production environments
                    )
                    hods_to_add.append(hod)
                
                # Bulk Database Save
                if hods_to_add:
                    db.session.bulk_save_objects(hods_to_add)
                    db.session.commit()
                    flash(f'Successfully imported {len(hods_to_add)} HOD records!', 'success')
                
                if duplicate_errors:
                    for err in duplicate_errors:
                        flash(err, 'warning')
                        
                return redirect(url_for('admin_page', id=current_user.id))
                
            except Exception as e:
                db.session.rollback()
                flash(f"Error parsing file: {str(e)}", 'danger')
                return redirect(request.url)
                
        else:
            flash('Invalid format! Please use a valid .csv, .xlsx, or .xls file.', 'danger')
            return redirect(request.url)
            
    return render_template('hod_bulk_import.html')

# --- Route for Staff File Upload & Processing ---
@bulk_import_file.route('/upload_staff', methods=['GET', 'POST'])
def upload_staff():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part in the request.', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected. Please choose a file.', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            
            try:
                # Force specific columns to be read as strings to preserve formatting
                string_columns = ['username', 'password']
                converters = {col: str for col in string_columns}
                
                # Parse based on file type
                if file_ext == 'csv':
                    df = pd.read_csv(file, converters=converters)
                else:
                    df = pd.read_excel(file, converters=converters)
                
                # Clean header spacing
                df.columns = df.columns.str.strip()
                df = df.where(pd.notnull(df), None)
                
                staff_to_add = []
                duplicate_errors = []
                
                # Iterate rows and extract data
                for index, row in df.iterrows():
                    username_val = str(row.get('username', '')).strip() if row.get('username') else None
                    name_val = str(row.get('name', '')).strip() if row.get('name') else None
                    dept_val = str(row.get('department', '')).strip() if row.get('department') else None
                    password_val = str(row.get('password', '')).strip() if row.get('password') else None
                    
                    # Validate required constraints
                    if not username_val or not name_val or not password_val:
                        continue # Skip bad/empty rows
                        
                    # Check for unique username constraint violation
                    existing = Staff.query.filter_by(username=username_val).first()
                    if existing:
                        duplicate_errors.append(f"Row {index + 2}: Username '{username_val}' already exists. Skipped.")
                        continue
                    
                    staff = Staff(
                        username=username_val,
                        name=name_val,
                        department=dept_val,
                        password=password_val
                    )
                    staff_to_add.append(staff)
                
                # Commit valid rows dynamically
                if staff_to_add:
                    db.session.bulk_save_objects(staff_to_add)
                    db.session.commit()
                    flash(f'Successfully imported {len(staff_to_add)} Staff records!', 'success')
                
                if duplicate_errors:
                    for err in duplicate_errors:
                        flash(err, 'warning')
                        
                return redirect(url_for('admin_page', id=current_user.id))
                
            except Exception as e:
                db.session.rollback()
                flash(f"Error parsing file: {str(e)}", 'danger')
                return redirect(request.url)
                
        else:
            flash('Invalid format! Please use a valid .csv, .xlsx, or .xls file.', 'danger')
            return redirect(request.url)
            
    return render_template('staff_bulk_import.html')

# --- Route for Warden File Upload & Processing ---
@bulk_import_file.route('/upload_warden', methods=['GET', 'POST'])
def upload_warden():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part in the request.', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected. Please choose a file.', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            
            try:
                # Force username and password columns to remain as string datatypes
                string_columns = ['username', 'password']
                converters = {col: str for col in string_columns}
                
                # Parse depending on layout format
                if file_ext == 'csv':
                    df = pd.read_csv(file, converters=converters)
                else:
                    df = pd.read_excel(file, converters=converters)
                
                # Clean up accidental whitespace padding from headers
                df.columns = df.columns.str.strip()
                df = df.where(pd.notnull(df), None)
                
                wardens_to_add = []
                duplicate_errors = []
                
                # Loop through sheet rows
                for index, row in df.iterrows():
                    username_val = str(row.get('username', '')).strip() if row.get('username') else None
                    name_val = str(row.get('name', '')).strip() if row.get('name') else None
                    password_val = str(row.get('password', '')).strip() if row.get('password') else None
                    
                    # Validate that required elements are not missing
                    if not username_val or not name_val or not password_val:
                        continue # Skip empty or invalid rows safely
                        
                    # Prevent database crashes due to duplicate unique keys
                    existing = Warden.query.filter_by(username=username_val).first()
                    if existing:
                        duplicate_errors.append(f"Row {index + 2}: Username '{username_val}' already exists. Skipped.")
                        continue
                    
                    warden = Warden(
                        username=username_val,
                        name=name_val,
                        password=password_val
                    )
                    wardens_to_add.append(warden)
                
                # Efficient bulk transaction commit
                if wardens_to_add:
                    db.session.bulk_save_objects(wardens_to_add)
                    db.session.commit()
                    flash(f'Successfully imported {len(wardens_to_add)} Warden records!', 'success')
                
                if duplicate_errors:
                    for err in duplicate_errors:
                        flash(err, 'warning')
                        
                return redirect(url_for('admin_page', id=current_user.id))
                
            except Exception as e:
                db.session.rollback()
                flash(f"Error parsing file: {str(e)}", 'danger')
                return redirect(request.url)
                
        else:
            flash('Invalid format! Please use a valid .csv, .xlsx, or .xls file.', 'danger')
            return redirect(request.url)
            
    return render_template('warden_bulk_import.html')
