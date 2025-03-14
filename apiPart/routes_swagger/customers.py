from flask import Blueprint, request, jsonify
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import get_db_connection

customers_bp = Blueprint('customers', __name__)
api = Namespace('Customers', description='Customer-related operations')

# Swagger model definition
customer_model = api.model('Customer', {
    'name': fields.String(required=True, description='Customer name'),
    'phone': fields.String(required=True, description='Customer phone number'),
    'e_mail': fields.String(required=True, description='Customer email address'),
})

@api.route('/')
class CustomerList(Resource):
    @api.doc('list_customers', responses={
        200: 'Success',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def get(self):
        """List all customers"""
        claims = get_jwt()
        if claims['role'] != 'admin':
            return {"message": "Access denied"}, 403

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM customers")
            customers = cursor.fetchall()
        except Exception as e:
            db.close()
            return {"message": "Error retrieving customers", "error": str(e)}, 500

        db.close()
        return customers, 200

    @api.expect(customer_model)
    @api.doc('add_customer', responses={
        201: 'Customer added successfully!',
        400: 'A customer with this email already exists',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def post(self):
        """Add a new customer"""
        claims = get_jwt()
        if claims['role'] != 'admin':
            return {"message": "Access denied"}, 403

        data = request.json
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM customers WHERE e_mail = %s", (data['e_mail'],))
        existing_customer = cursor.fetchone()
        if existing_customer:
            db.close()
            return {"message": "A customer with this email already exists"}, 400

        try:
            cursor.execute("INSERT INTO customers (name, phone, e_mail) VALUES (%s, %s, %s)",
                           (data['name'], data['phone'], data['e_mail']))
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error adding customer", "error": str(e)}, 500

        db.close()
        return {"message": "Customer added successfully!"}, 201

@api.route('/me')
class CustomerProfile(Resource):
    @api.doc('get_my_profile', responses={
        200: 'Success',
        403: 'Access Denied',
        404: 'User not found',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def get(self):
        """Get current user's profile"""
        current_user = get_jwt_identity()
        claims = get_jwt()

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM customers WHERE e_mail = %s", (current_user,))
            user_data = cursor.fetchone()
        except Exception as e:
            db.close()
            return {"message": "Error retrieving user data", "error": str(e)}, 500

        db.close()
        if not user_data:
            return {"message": "User not found"}, 404

        return user_data, 200

@api.route('/<int:customer_id>')
class Customer(Resource):
    @api.doc('get_customer', responses={
        200: 'Success',
        403: 'Access Denied',
        404: 'Customer not found',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def get(self, customer_id):
        """Get a specific customer by ID"""
        claims = get_jwt()
        if claims['role'] != 'admin' and claims['id'] != customer_id:
            return {"message": "Access denied"}, 403

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
            customer = cursor.fetchone()
        except Exception as e:
            db.close()
            return {"message": "Error retrieving customer data", "error": str(e)}, 500

        db.close()
        if not customer:
            return {"message": "Customer not found"}, 404

        return customer, 200

    @api.expect(customer_model)
    @api.doc('update_customer', responses={
        200: 'Customer updated successfully!',
        400: 'A customer with this email already exists',
        403: 'Access Denied',
        404: 'Customer not found',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def put(self, customer_id):
        """Update a customer"""
        claims = get_jwt()
        current_user_id = claims['id']
        current_role = claims['role']

        # Restrict non-admin users to update only their own data
        if current_role != 'admin' and current_user_id != customer_id:
            return {"message": "Access denied: You can only update your own profile"}, 403

        data = request.json
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Check if the customer exists
        cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
        customer = cursor.fetchone()
        if not customer:
            db.close()
            return {"message": "Customer not found"}, 404

        # Check if the email being updated already exists for another customer
        cursor.execute("SELECT * FROM customers WHERE e_mail = %s AND customer_id != %s", (data['e_mail'], customer_id))
        existing_customer = cursor.fetchone()
        if existing_customer:
            db.close()
            return {"message": "A customer with this email already exists"}, 400

        try:
            # Update the customer information
            cursor.execute(
                "UPDATE customers SET name = %s, phone = %s, e_mail = %s WHERE customer_id = %s",
                (data['name'], data['phone'], data['e_mail'], customer_id)
            )
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error updating customer", "error": str(e)}, 500

        db.close()
        return {"message": "Customer updated successfully!"}, 200

    @api.doc('delete_customer', responses={
        200: 'Customer deleted successfully!',
        403: 'Access Denied',
        404: 'Customer not found',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def delete(self, customer_id):
        """Delete a customer"""
        claims = get_jwt()
        if claims['role'] != 'admin':
            return {"message": "Access denied"}, 403

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
        customer = cursor.fetchone()
        if not customer:
            db.close()
            return {"message": "Customer not found"}, 404

        try:
            cursor.execute("DELETE FROM customers WHERE customer_id = %s", (customer_id,))
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error deleting customer", "error": str(e)}, 500

        db.close()
        return {"message": "Customer deleted successfully!"}, 200
