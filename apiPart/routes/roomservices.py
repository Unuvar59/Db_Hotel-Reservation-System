from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import get_db_connection

roomservices_bp = Blueprint('roomservices', __name__)

@roomservices_bp.route('/', methods=['GET'])
@jwt_required()
def get_roomservices():
    claims = get_jwt()
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM roomservices")
    roomservices = cursor.fetchall()
    db.close()
    return jsonify(roomservices)

@roomservices_bp.route('/', methods=['POST'])
@jwt_required()
def add_roomservice():
    claims = get_jwt()
    if claims['role'] != 'admin':
        return jsonify({"message": "Access denied"}), 403

    data = request.json
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("INSERT INTO roomservices (room_id, service_type, cost) VALUES (%s, %s, %s)",
                   (data['room_id'], data['service_type'], data['cost']))
    db.commit()
    db.close()
    return jsonify({"message": "Room service added successfully!"}), 201

@roomservices_bp.route('/<int:service_id>', methods=['PUT'])
@jwt_required()
def update_roomservice(service_id):
    claims = get_jwt()
    if claims['role'] != 'admin':
        return jsonify({"message": "Access denied"}), 403

    data = request.json
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("UPDATE roomservices SET room_id = %s, service_type = %s, cost = %s WHERE service_id = %s",
                   (data['room_id'], data['service_type'], data['cost'], service_id))
    db.commit()
    db.close()
    return jsonify({"message": "Room service updated successfully!"})

@roomservices_bp.route('/<int:service_id>', methods=['DELETE'])
@jwt_required()
def delete_roomservice(service_id):
    claims = get_jwt()
    if claims['role'] != 'admin':
        return jsonify({"message": "Access denied"}), 403

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("DELETE FROM roomservices WHERE service_id = %s", (service_id,))
    db.commit()
    db.close()
    return jsonify({"message": "Room service deleted successfully!"})