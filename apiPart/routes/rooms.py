from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import get_db_connection

rooms_bp = Blueprint('rooms', __name__)

@rooms_bp.route('/', methods=['GET'])
@jwt_required()
def get_rooms():
    claims = get_jwt()
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM rooms")
    rooms = cursor.fetchall()
    db.close()
    return jsonify(rooms)

@rooms_bp.route('/', methods=['POST'])
@jwt_required()
def add_room():
    claims = get_jwt()
    if claims['role'] != 'admin':
        return jsonify({"message": "Access denied"}), 403

    data = request.json
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("INSERT INTO rooms (type, pricing, capacity) VALUES (%s, %s, %s)",
                   (data['type'], data['pricing'], data['capacity']))
    db.commit()
    db.close()
    return jsonify({"message": "Room added successfully!"}), 201

@rooms_bp.route('/<int:room_id>', methods=['PUT'])
@jwt_required()
def update_room(room_id):
    claims = get_jwt()
    if claims['role'] != 'admin':
        return jsonify({"message": "Access denied"}), 403

    data = request.json
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("UPDATE rooms SET type = %s, pricing = %s, capacity = %s WHERE room_id = %s",
                   (data['type'], data['pricing'], data['capacity'], room_id))
    db.commit()
    db.close()
    return jsonify({"message": "Room updated successfully!"})

@rooms_bp.route('/<int:room_id>', methods=['DELETE'])
@jwt_required()
def delete_room(room_id):
    claims = get_jwt()
    if claims['role'] != 'admin':
        return jsonify({"message": "Access denied"}), 403

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("DELETE FROM rooms WHERE room_id = %s", (room_id,))
    db.commit()
    db.close()
    return jsonify({"message": "Room deleted successfully!"})