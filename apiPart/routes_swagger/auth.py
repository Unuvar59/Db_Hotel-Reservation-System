from flask_restx import Namespace, Resource, fields
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models.database import get_db_connection
from datetime import timedelta

auth_ns = Namespace('Auth', description='Authentication related operations')

# Swagger model for login
login_model = auth_ns.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
})

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.doc('login_user', description="""
        Login with registered credentials.
    """)
    def post(self):
        """Login a user and return JWT token"""
        try:
            data = request.json
            email = data.get("email")
            password = data.get("password")

            # Fetch user from the database
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE mail = %s", (email,))
            user = cursor.fetchone()
            db.close()

            # Check if user exists and password is correct
            if user and user['password'] == password:
                # Generate JWT token
                access_token = create_access_token(
                    identity=email,
                    additional_claims={
                        "id": user['id'],
                        "role": user['role']
                    },
                    expires_delta=timedelta(hours=1)
                )
                return {"token": access_token}, 200

            return {"message": "Invalid email or password"}, 401
        except Exception as e:
            return {"message": "An error occurred during login", "error": str(e)}, 500
        


# Swagger model for sign up

signup_model = auth_ns.model('SignUp', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
    'name': fields.String(required=True, description='User name'),
    'phone': fields.String(required=True, description='User phone'),
})

@auth_ns.route('/signup')
class SignUp(Resource):
    @auth_ns.expect(signup_model)
    @auth_ns.doc('sign_up_user', description="Register a new user")
    def post(self):
        """Register a new user"""
        try:
            data = request.json
            email = data.get("email")
            password = data.get("password")
            name = data.get("name")
            phone = data.get("phone")

            # Check if the email already exists
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)

            # Check if the email already exists in users table
            cursor.execute("SELECT * FROM users WHERE mail = %s", (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                return {"message": "Email already registered"}, 400

            # Check if the email exists in customers table
            cursor.execute("SELECT * FROM customers WHERE e_mail = %s", (email,))
            existing_customer = cursor.fetchone()

            if existing_customer:
                # If customer exists, only add to users table
                cursor.execute(
                    "INSERT INTO users (mail, password, role) VALUES (%s, %s, %s)",
                    (email, password, 'user')
                )
                db.commit()
                db.close()
                return {"message": "User registered successfully (linked to existing customer)"}, 201
            else:
                # If customer doesn't exist, add to both customers and users tables
                cursor.execute(
                    "INSERT INTO customers (name, phone, e_mail) VALUES (%s, %s, %s)",
                    (name, phone, email)
                )
                db.commit()

                cursor.execute(
                    "INSERT INTO users (mail, password, role) VALUES (%s, %s, %s)",
                    (email, password, 'user')
                )
                db.commit()
                db.close()
                return {"message": "User registered successfully (new customer created)"}, 201
        except Exception as e:
            return {"message": "An error occurred during sign up", "error": str(e)}, 500
