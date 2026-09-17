from flask import Blueprint, request, jsonify
from flask_login import login_required
import math

location_bp = Blueprint('location', __name__)

PERMITTED_LAT = 12.5702 
PERMITTED_LNG = 79.4338
MAX_RADIUS_KM = 15.0

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2)**2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@location_bp.route('/request_letter', methods=['POST'])
@login_required
def request_letter():
    data = request.get_json() or {}
    user_lat = data.get('user_lat')
    user_lon = data.get('user_lon')
    student_id = data.get('student_id')
    check_only = data.get('check_only', False)

    if user_lat is None or user_lon is None:
        return jsonify({"status": "error", "reason": "Location coordinates missing."}), 400

    try:
        lat = float(user_lat)
        lon = float(user_lon)
    except (ValueError, TypeError):
        return jsonify({"status": "error", "reason": "Invalid coordinate format."}), 400

    distance = calculate_distance(lat, lon, PERMITTED_LAT, PERMITTED_LNG)

    if distance <= MAX_RADIUS_KM:
        # If this was just a background eligibility check from window.onload:
        if check_only:
            return jsonify({
                "status": "success",
                "message": "Eligible to request letter."
            }), 200

        # If check_only is False, perform DB insertion here (e.g. Letter creation):
        # new_letter = Letter(student_id=student_id, ...)
        # db.session.add(new_letter)
        # db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Inside campus zone. Letter request submitted successfully!"
        }), 200
    else:
        return jsonify({
            "status": "blocked",
            "reason": f"Access denied. You are {distance:.2f} km outside the permitted zone."
        }), 403