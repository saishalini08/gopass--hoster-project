from flask import Blueprint,Flask, request, jsonify,render_template
import math

location_bp = Blueprint("location",__name__)

# Geofencing configuration (in meters)
# The user MUST be within this radius to proceed.
PERMITTED_RADIUS = 100  

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    R = 6371000.0  # Earth radius in meters

    # Convert coordinates from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Difference in coordinates
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

@location_bp.route('/book_ticket', methods=['POST'])
def book_ticket():
    data = request.get_json()
    
    # Extract user coordinates from the request payload (sent by JavaScript)
    user_lat = data.get('user_lat')
    user_lon = data.get('user_lon')
    
    # The target coordinates the user must be near
    target_lat = data.get('target_lat') 
    target_lon = data.get('target_lon')

    if None in (user_lat, user_lon, target_lat, target_lon):
        return jsonify({"error": "Missing coordinate data"}), 400

    # Calculate distance
    distance = calculate_haversine_distance(user_lat, user_lon, target_lat, target_lon)
    
    # REVERSED GEOFENCE LOGIC: Must be INSIDE the radius
    if distance <= PERMITTED_RADIUS:
        return jsonify({
            "status": "success",
            "message": "You are within the permitted zone. Access granted.",
            "distance_meters": round(distance, 2)
        }), 200
        
    else:
        return jsonify({
            "status": "failed",
            "reason": f"Access denied. You are {round(distance, 2)} meters away. You must be within {PERMITTED_RADIUS} meters of the target location.",
            "distance_meters": round(distance, 2)
        }), 403

