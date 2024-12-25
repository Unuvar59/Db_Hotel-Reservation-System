from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import get_db_connection

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/', methods=['GET'])
@jwt_required()
def get_payments():
    claims = get_jwt()
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if claims['role'] == 'admin':
        # Admin tüm ödemeleri görebilir
        cursor.execute("SELECT * FROM payments")
        payments = cursor.fetchall()
    else:
        # Kullanıcı yalnızca kendi ödemelerini görebilir
        current_user_id = claims['id']
        cursor.execute("""
            SELECT payments.* FROM payments
            JOIN reservations ON payments.reservation_id = reservations.reservation_id
            WHERE reservations.customer_id = %s
        """, (current_user_id,))
        payments = cursor.fetchall()

    db.close()
    return jsonify(payments)

@payments_bp.route('/', methods=['POST'])
@jwt_required()
def add_payment():
    claims = get_jwt()
    data = request.json
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Rezervasyonun varlığını ve kullanıcının yetkisini kontrol et
    cursor.execute("SELECT * FROM reservations WHERE reservation_id = %s", (data['reservation_id'],))
    reservation = cursor.fetchone()
    if not reservation:
        db.close()
        return jsonify({"message": "Invalid reservation_id: Reservation does not exist"}), 400

    # Kullanıcı yalnızca kendi rezervasyonları için ödeme yapabilir
    if claims['role'] != 'admin' and reservation['customer_id'] != claims['id']:
        db.close()
        return jsonify({"message": "You are not authorized to add payment for this reservation"}), 403

    # Ödeme ekle
    cursor.execute(
        "INSERT INTO payments (reservation_id, amount, payment_date) VALUES (%s, %s, %s)",
        (data['reservation_id'], data['amount'], data['payment_date'])
    )
    db.commit()
    db.close()
    return jsonify({"message": "Payment added successfully!"}), 201

@payments_bp.route('/<int:payment_id>', methods=['DELETE'])
@jwt_required()
def delete_payment(payment_id):
    claims = get_jwt()
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Ödeme bilgilerini al
    cursor.execute("SELECT * FROM payments WHERE payment_id = %s", (payment_id,))
    payment = cursor.fetchone()
    if not payment:
        db.close()
        return jsonify({"message": "Invalid payment_id: Payment does not exist"}), 400

    # Rezervasyonun bilgilerini kontrol et
    cursor.execute("""
        SELECT * FROM reservations WHERE reservation_id = %s
    """, (payment['reservation_id'],))
    reservation = cursor.fetchone()

    if not reservation:
        db.close()
        return jsonify({"message": "Invalid reservation associated with this payment"}), 400

    # Admin olmayan kullanıcılar yalnızca kendi rezervasyonlarına ait ödemeleri silebilir
    if claims['role'] != 'admin' and reservation['customer_id'] != claims['id']:
        db.close()
        return jsonify({"message": "You are not authorized to delete this payment"}), 403

    # Ödemeyi sil
    cursor.execute("DELETE FROM payments WHERE payment_id = %s", (payment_id,))
    db.commit()
    db.close()

    return jsonify({"message": "Payment deleted successfully!"})
