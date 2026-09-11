from flask import Blueprint, render_template, redirect, request,url_for, flash, jsonify
from flask_login import login_user, login_required, current_user, logout_user
import json
from datetime import datetime
import re
from models import db, User, Student, Warden, Security, Staff, HOD, Admin, Letter, DetailedPass 

security_bp = Blueprint('security',__name__)

#Security
@security_bp.route('/security_login',methods=['GET','POST'])
def security() :
    if request.method == 'POST' :
        security = Security.query.filter_by(username=request.form.get('username')).first()
        if security and security.password == request.form.get('password') :
            login_user(security)
            return redirect(url_for('security.security_page',id=security.id))
    return render_template('security/security_login.html')


@security_bp.route('/security_page/<int:id>', methods=['GET', 'POST'])
@login_required
def security_page(id):
    if current_user.id != id:
        return render_template('error_page.html')
    security = Security.query.get_or_404(id)
    records = DetailedPass.query.order_by(DetailedPass.scanned_at.desc()).all()
    return render_template('security/security_page.html', security=security, records=records)

def get_val(pattern, text):
    """Extracts values based on your specific QR format labels."""
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else "N/A"

@security_bp.route('/open_scanner')
def open_scanner():
    records = DetailedPass.query.order_by(DetailedPass.scanned_at.desc()).all()
    return render_template('scanner/scanner.html', records=records)

@security_bp.route('/verify_id', methods=['POST'])
def verify_id():
    letter_id = request.form.get('letter_id')
    
    # 1. Check if the ID was actually provided
    if not letter_id:
        flash("Please enter a Letter ID to verify.", "warning")
        return redirect(url_for('security.open_scanner'))
        
    # 2. Query the database for the letter
    letter = Letter.query.filter_by(id=letter_id).first()
    if letter:
        student = letter.student  # Automatically fetches the linked Student object
    
    # 3. Check if the letter exists and if it is 'Approved'
    if not letter or letter.status != 'Approved':
        # If it exists but is already complete, give a specific message
        if letter and letter.status == 'Complete':
            flash(f"Already Scanned Completed {letter.id}", "warning")
        else:
            flash("Invalid Letter ID or not approved.", "error")
        return redirect(url_for('security.open_scanner'))
    
    # 4. Process the valid, approved letter
    letter.status = 'Complete'
    
    # 5. Create the new DetailedPass record
    new_record = DetailedPass(
        letter_id=letter.id,
        student_name=letter.student_name,
        dept=letter.student_department,
        year=letter.student_year,
        scanned_at=datetime.utcnow()  # Note: Use timezone-aware dates if possible in your app
    )
    
    # 6. Commit both changes to the database in one transaction
    try:
        db.session.add(new_record)
        db.session.commit()
        flash(f"Gate pass for {letter.student_name} verified successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while saving the data.", "error")
        # Optional: log the error `e` here
        
    return redirect(url_for('security.open_scanner'))

@security_bp.route('/save_scan', methods=['POST'])
def save_scan():
    data = request.get_json()
    raw_text = data.get('qr_text', '')

    if not raw_text:
        return jsonify({"status": "error", "message": "No data received"}), 400

    try:
        # 1. Parse the JSON from the QR code
        q = json.loads(raw_text)
        
        # 2. Map JSON keys to your DetailedPass Database Columns
        new_record = DetailedPass(
            letter_id      = str(q.get("ID", "")),
            student_name   = q.get("Student Name", "Unknown"),
            dept           = q.get("Department", ""),
            year           = str(q.get("Year", "")),
            scanned_at     = datetime.utcnow() # Records exactly when security scanned it
        )

        db.session.add(new_record)
        db.session.commit()
        
        return jsonify({
            "status": "success", 
            "message": f"Pass verified for {new_record.student_name}"
        }), 200

    except json.JSONDecodeError:
        return jsonify({"status": "error", "message": "Invalid QR Format. Please use the updated Gate Pass."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
