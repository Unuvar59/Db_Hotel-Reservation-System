from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import get_db_connection

customerevents_bp = Blueprint('customerevents', __name__)

@customerevents_bp.route('/', methods=['GET'])
@jwt_required()
def get_customerevents():
    claims = get_jwt()
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customerevents")
    customerevents = cursor.fetchall()
    db.close()
    return jsonify(customerevents)

@customerevents_bp.route('/', methods=['POST'])
@jwt_required()
def add_customerevent():
    claims = get_jwt()
    data = request.json
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("INSERT INTO customerevents (customer_id, event_id, participation_date) VALUES (%s, %s, %s)",
                   (data['customer_id'], data['event_id'], data['participation_date']))
    db.commit()
    db.close()
    return jsonify({"message": "Customer event added successfully!"}), 201

@customerevents_bp.route('/<int:customerevent_id>', methods=['PUT'])
@jwt_required()
def update_customerevent(customerevent_id):
    claims = get_jwt()
    data = request.json
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("UPDATE customerevents SET customer_id = %s, event_id = %s, participation_date = %s WHERE customerevent_id = %s",
                   (data['customer_id'], data['event_id'], data['participation_date'], customerevent_id))
    db.commit()
    db.close()
    return jsonify({"message": "Customer event updated successfully!"})

@customerevents_bp.route('/<int:customerevent_id>', methods=['DELETE'])
@jwt_required()
def delete_customerevent(customerevent_id):
    claims = get_jwt()
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("DELETE FROM customerevents WHERE customerevent_id = %s", (customerevent_id,))
    db.commit()
    db.close()
    return jsonify({"message": "Customer event deleted successfully!"})