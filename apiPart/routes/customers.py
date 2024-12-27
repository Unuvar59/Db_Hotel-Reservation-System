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
    @api.doc('list_customers')
    @jwt_required()
    def get(self):
        """List all customers"""
        claims = get_jwt()
        if claims['role'] != 'admin':
            return {"message": "Access denied"}, 403

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM customers")
        customers = cursor.fetchall()
        db.close()
        return customers
    
    @api.expect(customer_model)
    @api.doc('add_customer')
    @jwt_required()
    def post(self):
        """Add a new customer"""
        claims = get_jwt()
        if claims['role'] != 'admin':
            return {"message": "Access denied"}, 403

        data = request.json
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # check if the email address already exists
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


@api.route('/<int:customer_id>')
class Customer(Resource):
    @api.doc('get_customer')
    @jwt_required()
    def get(self, customer_id):
        """Get a specific customer by ID"""
        claims = get_jwt()
        if claims['role'] != 'admin' and claims['id'] != customer_id:
            return {"message": "Access denied"}, 403

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
        customer = cursor.fetchone()
        db.close()

        if not customer:
            return {"message": "Customer not found"}, 404

        return customer

    @api.expect(customer_model)
    @api.doc('update_customer')
    @jwt_required()
    def put(self, customer_id):
        """Update a customer"""
        claims = get_jwt()
        if claims['role'] != 'admin' and claims['id'] != customer_id:
            return {"message": "You are not authorized to update this customer"}, 403

        data = request.json
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # check if the email address which will be updated is not belonging to another customer
        cursor.execute("SELECT * FROM customers WHERE e_mail = %s AND customer_id != %s", (data['e_mail'], customer_id))
        existing_customer = cursor.fetchone()
        if existing_customer:
            db.close()
            return {"message": "A customer with this email already exists"}, 400

        try:
            cursor.execute(
                "UPDATE customers SET name = %s, phone = %s, e_mail = %s WHERE customer_id = %s",
                (data['name'], data['phone'], data['e_mail'], customer_id)
            )
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error updating customer", "error": str(e)}, 500

        db.close()
        return {"message": "Customer updated successfully!"}

    @api.doc('delete_customer')
    @jwt_required()
    def delete(self, customer_id):
        """Delete a customer"""
        claims = get_jwt()
        if claims['role'] != 'admin':
            return {"message": "Access denied"}, 403

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # check if the customer exists before deleting
        cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
        customer = cursor.fetchone()
        if not customer:
            db.close()
            return {"message": "Customer does not exist"}, 404

        try:
            cursor.execute("DELETE FROM customers WHERE customer_id = %s", (customer_id,))
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error deleting customer", "error": str(e)}, 500

        db.close()
        return {"message": "Customer deleted successfully!"}

# @customers_bp.route('/', methods=['GET'])
# @jwt_required()
# def get_customers():
#     claims = get_jwt()
#     if claims['role'] != 'admin':
#         return jsonify({"message": "Access denied"}), 403

#     db = get_db_connection()
#     cursor = db.cursor(dictionary=True)

#     try:
#         cursor.execute("SELECT * FROM customers")
#         customers = cursor.fetchall()
#     except Exception as e:
#         db.close()
#         return jsonify({"message": "Error retrieving customers", "error": str(e)}), 500

#     db.close()

#     if not customers:
#         return jsonify({"message": "No customers found"}), 404

#     return jsonify(customers)

# @customers_bp.route('/me', methods=['GET'])
# @jwt_required()
# def get_my_profile():
#     current_user = get_jwt_identity()
#     claims = get_jwt()
#     db = get_db_connection()
#     cursor = db.cursor(dictionary=True)
#     if claims['role'] == 'admin':
#         return jsonify({"message": "You are a admin"}), 500
#     try:
#         cursor.execute("SELECT * FROM customers WHERE e_mail = %s", (current_user,))
#         user_data = cursor.fetchone()
#     except Exception as e:
#         db.close()
#         return jsonify({"message": "Error retrieving user data", "error": str(e)}), 500

#     db.close()

#     if not user_data:
#         return jsonify({"message": "User not found"}), 404

#     return jsonify(user_data)

# @customers_bp.route('/', methods=['POST'])
# @jwt_required()
# def add_customer():
#     claims = get_jwt()
#     if claims['role'] != 'admin':
#         return jsonify({"message": "Access denied"}), 403

#     data = request.json

#     db = get_db_connection()
#     cursor = db.cursor(dictionary=True)

#     # Email adresinin zaten mevcut olup olmadığını kontrol et
#     cursor.execute("SELECT * FROM customers WHERE e_mail = %s", (data['e_mail'],))
#     existing_customer = cursor.fetchone()
#     if existing_customer:
#         db.close()
#         return jsonify({"message": "A customer with this email already exists"}), 400

#     try:
#         cursor.execute("INSERT INTO customers (name, phone, e_mail) VALUES (%s, %s, %s)",
#                        (data['name'], data['phone'], data['e_mail']))
#         db.commit()
#     except Exception as e:
#         db.close()
#         return jsonify({"message": "Error adding customer", "error": str(e)}), 500

#     db.close()
#     return jsonify({"message": "Customer added successfully!"}), 201

# @customers_bp.route('/<int:customer_id>', methods=['PUT'])
# @jwt_required()
# def update_customer(customer_id):
#     claims = get_jwt()
#     current_user = get_jwt_identity()
#     data = request.json

#     db = get_db_connection()
#     cursor = db.cursor(dictionary=True)

#     # Kullanıcı admin değilse yalnızca kendi bilgilerini değiştirebilir
#     if claims['role'] != 'admin' and claims['id'] != customer_id:
#         db.close()
#         return jsonify({"message": "You are not authorized to update this customer"}), 403

#     # Güncellenen e-posta adresinin başka bir kullanıcıya ait olmadığını kontrol et
#     cursor.execute("SELECT * FROM customers WHERE e_mail = %s AND customer_id != %s", (data['e_mail'], customer_id))
#     existing_customer = cursor.fetchone()
#     if existing_customer:
#         db.close()
#         return jsonify({"message": "A customer with this email already exists"}), 400

#     try:
#         # Kullanıcı bilgilerini güncelle
#         cursor.execute(
#             "UPDATE customers SET name = %s, phone = %s, e_mail = %s WHERE customer_id = %s",
#             (data['name'], data['phone'], data['e_mail'], customer_id)
#         )
#         db.commit()
#     except Exception as e:
#         db.close()
#         return jsonify({"message": "Error updating customer", "error": str(e)}), 500

#     db.close()
#     return jsonify({"message": "Customer updated successfully!"}), 200

# @customers_bp.route('/<int:customer_id>', methods=['DELETE'])
# @jwt_required()
# def delete_customer(customer_id):
#     claims = get_jwt()
#     db = get_db_connection()
#     cursor = db.cursor(dictionary=True)

#     if claims['role'] != 'admin':
#         db.close()
#         return jsonify({"message": "Access denied"}), 403

#     # Silinecek kullanıcıyı kontrol et
#     cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
#     customer = cursor.fetchone()
#     if not customer:
#         db.close()
#         return jsonify({"message": "Customer does not exist"}), 404

#     # Kullanıcıyı sil
#     try:
#         cursor.execute("DELETE FROM customers WHERE customer_id = %s", (customer_id,))
#         db.commit()
#     except Exception as e:
#         db.close()
#         return jsonify({"message": "Error deleting customer", "error": str(e)}), 500

#     db.close()
#     return jsonify({"message": "Customer deleted successfully!"}), 200
