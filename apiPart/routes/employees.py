from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import get_db_connection

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/', methods=['GET'])
@jwt_required()
def get_employees():
    claims = get_jwt()
    if claims['role'] != 'admin':
        return jsonify({"message": "Access denied"}), 403

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    db.close()
    return jsonify(employees)

@employees_bp.route('/', methods=['POST'])
@jwt_required()
def add_employee():
    claims = get_jwt()
    if claims['role'] != 'admin':
        return jsonify({"message": "Access denied"}), 403

    data = request.json
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("INSERT INTO employees (name, position, contact) VALUES (%s, %s, %s)",
                   (data['name'], data['position'], data['contact']))
    db.commit()
    db.close()
    return jsonify({"message": "Employee added successfully!"}), 201

@employees_bp.route('/<int:employee_id>', methods=['PUT'])
@jwt_required()
def update_employee(employee_id):
    claims = get_jwt()
    if claims['role'] != 'admin':
        return jsonify({"message": "Access denied"}), 403

    data = request.json
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("UPDATE employees SET name = %s, position = %s, contact = %s WHERE employee_id = %s",
                   (data['name'], data['position'], data['contact'], employee_id))
    db.commit()
    db.close()
    return jsonify({"message": "Employee updated successfully!"})

@employees_bp.route('/<int:employee_id>', methods=['DELETE'])
@jwt_required()
def delete_employee(employee_id):
    claims = get_jwt()
    if claims['role'] != 'admin':
        return jsonify({"message": "Access denied"}), 403

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("DELETE FROM employees WHERE employee_id = %s", (employee_id,))
    db.commit()
    db.close()
    return jsonify({"message": "Employee deleted successfully!"})