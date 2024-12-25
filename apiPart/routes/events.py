from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import get_db_connection

events_bp = Blueprint('events', __name__)

@events_bp.route('/', methods=['GET'])
@jwt_required()
def get_events():
    claims = get_jwt()
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()
    db.close()
    return jsonify(events)

@events_bp.route('/', methods=['POST'])
@jwt_required()
def add_event():
    claims = get_jwt()
    if claims['role'] != 'admin':
        return jsonify({"message": "Access denied"}), 403

    data = request.json
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("INSERT INTO events (event_name, date, participation_fee) VALUES (%s, %s, %s)",
                   (data['event_name'], data['date'], data['participation_fee']))
    db.commit()
    db.close()
    return jsonify({"message": "Event added successfully!"}), 201

@events_bp.route('/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_event(event_id):
    claims = get_jwt()
    if claims['role'] != 'admin':
        return jsonify({"message": "Access denied"}), 403

    data = request.json
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("UPDATE events SET event_name = %s, date = %s, participation_fee = %s WHERE event_id = %s",
                   (data['event_name'], data['date'], data['participation_fee'], event_id))
    db.commit()
    db.close()
    return jsonify({"message": "Event updated successfully!"})

@events_bp.route('/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_event(event_id):
    claims = get_jwt()
    if claims['role'] != 'admin':
        return jsonify({"message": "Access denied"}), 403

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("DELETE FROM events WHERE event_id = %s", (event_id,))
    db.commit()
    db.close()
    return jsonify({"message": "Event deleted successfully!"})