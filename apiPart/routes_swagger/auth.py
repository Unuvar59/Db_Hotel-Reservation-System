from flask_restx import Namespace, Resource, fields
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models.database import get_db_connection
from datetime import timedelta

auth_ns = Namespace('Auth', description='Authentication related operations')

USER_DATA = {
    "admin@example.com": {"password": "admin123", "role": "admin"},
    "user@example.com": {"password": "user123", "role": "user"},
    "user2@example.com": {"password": "user123", "role": "user"}
}

# Swagger model for login
login_model = auth_ns.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
})

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.doc('login_user', description="""
        Test credentials for login:
        - Admin: admin@example.com / admin123
        - User: user@example.com / user123
        - User2: user2@example.com / user123
    """)
    def post(self):
        """Login a user and return JWT token"""
        try:
            data = request.json
            email = data.get("email")
            password = data.get("password")

            if email in USER_DATA and USER_DATA[email]['password'] == password:
                # Check if the user is not an admin, get the customer_id from the database
                if USER_DATA[email]['role'] != 'admin':
                    try:
                        db = get_db_connection()  # check database connection
                    except Exception as e:
                        return {"message": "Database connection failed", "error": str(e)}, 500

                    cursor = db.cursor(dictionary=True)
                    cursor.execute("SELECT customer_id FROM customers WHERE e_mail = %s", (email,))
                    customer = cursor.fetchone()
                    db.close()

                    if not customer:
                        return jsonify({"message": "Customer not found in the database"}), 404

                    # create token for the user
                    access_token = create_access_token(
                        identity=email,  # Only email is used as a string
                        additional_claims={
                            "id": customer['customer_id'],  # additional information is added here
                            "role": USER_DATA[email]['role']
                        },
                        expires_delta=timedelta(hours=1)
                    )
                else:
                    # create token for the admin
                    access_token = create_access_token(
                        identity=email,  # Only email is used as a string
                        additional_claims={
                            "role": USER_DATA[email]['role']
                        },
                        expires_delta=timedelta(hours=1)
                    )

                return {"token": access_token}, 200

            return {"message": "Invalid email or password"}, 401
        except Exception as e:
            return {"message": "An error occurred during login", "error": str(e)}, 500
