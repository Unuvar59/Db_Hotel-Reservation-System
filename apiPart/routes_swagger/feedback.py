from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import get_db_connection
from datetime import datetime

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

    # Check if customer_id exists
    cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (data['customer_id'],))
    customer = cursor.fetchone()
    if not customer:
        db.close()
        return jsonify({"message": "Invalid customer_id: Customer does not exist"}), 400
    
    # Admin olmayan kullanıcılar yalnızca kendi etkinliklerini güncelleyebilir
    if claims['role'] != 'admin' and (customer['customer_id'] != claims['id']  or data['customer_id'] != claims['id']):
        db.close()
        return jsonify({"message": "You are not authorized to add this feedback"}), 403
    
    # Get current date
    feedback_date = datetime.now().strftime('%Y-%m-%d')

    cursor.execute("INSERT INTO feedback (customer_id, feedback_details, feedback_date) VALUES (%s, %s, %s)",
                   (data['customer_id'], data['feedback_details'], feedback_date))
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

    # Check if customer_id exists
    cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (data['customer_id'],))
    customer = cursor.fetchone()
    if not customer:
        db.close()
        return jsonify({"message": "Invalid customer_id: Customer does not exist"}), 400
    
    # Admin olmayan kullanıcılar yalnızca kendi etkinliklerini güncelleyebilir
    if claims['role'] != 'admin' and (customer['customer_id'] != claims['id']  or data['customer_id'] != claims['id']):
        db.close()
        return jsonify({"message": "You are not authorized to update this feedback"}), 403
    
    cursor.execute("UPDATE feedback SET customer_id = %s, feedback_details = %s, feedback_date = %s WHERE feedback_id = %s",
                   (data['customer_id'], data['feedback_details'], data.get('feedback_date', datetime.now().strftime('%Y-%m-%d')), feedback_id))
    db.commit()
    db.close()
    return jsonify({"message": "Feedback updated successfully!"})

@feedback_bp.route('/<int:feedback_id>', methods=['DELETE'])
@jwt_required()
def delete_feedback(feedback_id):
    claims = get_jwt()
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Silinecek feedback'in varlığını ve sahibini kontrol et
    cursor.execute("SELECT * FROM feedback WHERE feedback_id = %s", (feedback_id,))
    feedback = cursor.fetchone()

    if not feedback:
        db.close()
        return jsonify({"message": "Invalid feedback_id: Feedback does not exist"}), 400

    # Kullanıcı admin değilse sadece kendi feedback'ini silebilir
    if claims['role'] != 'admin' and feedback['customer_id'] != claims['id']:
        db.close()
        return jsonify({"message": "You are not authorized to delete this feedback"}), 403

    # Feedback'i sil
    cursor.execute("DELETE FROM feedback WHERE feedback_id = %s", (feedback_id,))
    db.commit()
    db.close()
    return jsonify({"message": "Feedback deleted successfully!"})
