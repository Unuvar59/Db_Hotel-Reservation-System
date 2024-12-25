from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import get_db_connection

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/', methods=['GET'])
@jwt_required()
def get_feedback():
    claims = get_jwt()
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM feedback")
    feedback = cursor.fetchall()
    db.close()
    return jsonify(feedback)

@feedback_bp.route('/', methods=['POST'])
@jwt_required()
def add_feedback():
    claims = get_jwt()
    data = request.json
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("INSERT INTO feedback (customer_id, feedback_details, feedback_date) VALUES (%s, %s, %s)",
                   (data['customer_id'], data['feedback_details'], data['feedback_date']))
    db.commit()
    db.close()
    return jsonify({"message": "Feedback added successfully!"}), 201

@feedback_bp.route('/<int:feedback_id>', methods=['PUT'])
@jwt_required()
def update_feedback(feedback_id):
    claims = get_jwt()
    data = request.json
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("UPDATE feedback SET customer_id = %s, feedback_details = %s, feedback_date = %s WHERE feedback_id = %s",
                   (data['customer_id'], data['feedback_details'], data['feedback_date'], feedback_id))
    db.commit()
    db.close()
    return jsonify({"message": "Feedback updated successfully!"})

@feedback_bp.route('/<int:feedback_id>', methods=['DELETE'])
@jwt_required()
def delete_feedback(feedback_id):
    claims = get_jwt()
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("DELETE FROM feedback WHERE feedback_id = %s", (feedback_id,))
    db.commit()
    db.close()
    return jsonify({"message": "Feedback deleted successfully!"})