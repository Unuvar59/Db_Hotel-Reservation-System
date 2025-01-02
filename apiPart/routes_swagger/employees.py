from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import get_db_connection
from flask_restx import Namespace, Resource, fields

employees_bp = Blueprint('employees', __name__)

# Swagger Namespace
api = Namespace('Employees', description='Operations related to employees')

# Swagger Model
employee_model = api.model('Employee', {
    'name': fields.String(required=True, description='Employee name'),
    'position': fields.String(required=True, description='Employee position'),
    'contact': fields.String(required=True, description='Employee contact information')
})

@api.route('/')
class EmployeeList(Resource):
    @api.doc('list_employees', responses={
        200: 'Success',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def get(self):
        """List all employees (Admin only)"""
        claims = get_jwt()
        if claims['role'] != 'admin':
            return {"message": "Access denied"}, 403

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM employees")
            employees = cursor.fetchall()
        except Exception as e:
            db.close()
            return {"message": "Error retrieving employees", "error": str(e)}, 500
        db.close()
        return employees, 200

    @api.expect(employee_model)
    @api.doc('add_employee', responses={
        201: 'Employee added successfully!',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def post(self):
        """Add a new employee (Admin only)"""
        claims = get_jwt()
        if claims['role'] != 'admin':
            return {"message": "Access denied"}, 403

        data = request.json
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("INSERT INTO employees (name, position, contact) VALUES (%s, %s, %s)",
                           (data['name'], data['position'], data['contact']))
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error adding employee", "error": str(e)}, 500
        db.close()
        return {"message": "Employee added successfully!"}, 201

@api.route('/<int:employee_id>')
class Employee(Resource):
    @api.expect(employee_model)
    @api.doc('update_employee', responses={
        200: 'Employee updated successfully!',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def put(self, employee_id):
        """Update an employee (Admin only)"""
        claims = get_jwt()
        if claims['role'] != 'admin':
            return {"message": "Access denied"}, 403

        data = request.json
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("UPDATE employees SET name = %s, position = %s, contact = %s WHERE employee_id = %s",
                           (data['name'], data['position'], data['contact'], employee_id))
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error updating employee", "error": str(e)}, 500
        db.close()
        return {"message": "Employee updated successfully!"}, 200

    @api.doc('delete_employee', responses={
        200: 'Employee deleted successfully!',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def delete(self, employee_id):
        """Delete an employee (Admin only)"""
        claims = get_jwt()
        if claims['role'] != 'admin':
            return {"message": "Access denied"}, 403

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("DELETE FROM employees WHERE employee_id = %s", (employee_id,))
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error deleting employee", "error": str(e)}, 500
        db.close()
        return {"message": "Employee deleted successfully!"}, 200