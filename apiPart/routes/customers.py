from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import get_db_connection

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/', methods=['GET'])
@jwt_required()
def get_customers():
    claims = get_jwt()
    if claims['role'] != 'admin':
        return jsonify({"message": "Access denied"}), 403

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM customers")
        customers = cursor.fetchall()
    except Exception as e:
        db.close()
        return jsonify({"message": "Error retrieving customers", "error": str(e)}), 500

    db.close()

    if not customers:
        return jsonify({"message": "No customers found"}), 404

    return jsonify(customers)

@customers_bp.route('/me', methods=['GET'])
@jwt_required()
def get_my_profile():
    current_user = get_jwt_identity()

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM customers WHERE e_mail = %s", (current_user['email'],))
        user_data = cursor.fetchone()
    except Exception as e:
        db.close()
        return jsonify({"message": "Error retrieving user data", "error": str(e)}), 500

    db.close()

    if not user_data:
        return jsonify({"message": "User not found"}), 404

    return jsonify(user_data)

@customers_bp.route('/', methods=['POST'])
@jwt_required()
def add_customer():
    claims = get_jwt()
    if claims['role'] != 'admin':
        return jsonify({"message": "Access denied"}), 403

    data = request.json

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Email adresinin zaten mevcut olup olmadığını kontrol et
    cursor.execute("SELECT * FROM customers WHERE e_mail = %s", (data['e_mail'],))
    existing_customer = cursor.fetchone()
    if existing_customer:
        db.close()
        return jsonify({"message": "A customer with this email already exists"}), 400

    try:
        cursor.execute("INSERT INTO customers (name, phone, e_mail) VALUES (%s, %s, %s)",
                       (data['name'], data['phone'], data['e_mail']))
        db.commit()
    except Exception as e:
        db.close()
        return jsonify({"message": "Error adding customer", "error": str(e)}), 500

    db.close()
    return jsonify({"message": "Customer added successfully!"}), 201
