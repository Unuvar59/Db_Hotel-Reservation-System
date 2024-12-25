from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models.database import get_db_connection
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)

USER_DATA = {
    "admin@example.com": {"password": "admin123", "role": "admin"},
    "user@example.com": {"password": "user123", "role": "user"},
    "user2@example.com": {"password": "user123", "role": "user"}
}

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if email in USER_DATA and USER_DATA[email]['password'] == password:
        # Kullanıcı admin değilse veritabanından customer_id'yi kontrol et
        if USER_DATA[email]['role'] != 'admin':
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT customer_id FROM customers WHERE e_mail = %s", (email,))
            customer = cursor.fetchone()
            db.close()

            if not customer:
                return jsonify({"message": "Customer not found in the database"}), 404

            # Kullanıcı için token oluştur
            access_token = create_access_token(
                identity=email,  # Sadece email string olarak kullanılıyor
                additional_claims={
                    "id": customer['customer_id'],  # Ek bilgiler buraya ekleniyor
                    "role": USER_DATA[email]['role']
                },
                expires_delta=timedelta(hours=1)
            )
        else:
            # Admin için token oluştur
            access_token = create_access_token(
                identity=email,  # Sadece email string olarak kullanılıyor
                additional_claims={
                    "role": USER_DATA[email]['role']
                },
                expires_delta=timedelta(hours=1)
            )

        return jsonify({"token": access_token}), 200

    return jsonify({"message": "Invalid email or password"}), 401
