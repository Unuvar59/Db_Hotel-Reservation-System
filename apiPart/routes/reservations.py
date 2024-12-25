from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import get_db_connection

reservations_bp = Blueprint('reservations', __name__)

@reservations_bp.route('/', methods=['GET'])
@jwt_required()
def get_reservations():
    current_user = get_jwt_identity()
    claims = get_jwt()
    if claims['role'] != 'admin':
        return jsonify({"message": "Access denied"}), 403

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reservations")
    reservations = cursor.fetchall()
    db.close()
    return jsonify(reservations)

@reservations_bp.route('/', methods=['POST'])
@jwt_required()
def add_reservation():
    current_user = get_jwt_identity()
    claims = get_jwt()
    data = request.json
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    if claims['role'] != 'admin':
        data['customer_id'] = claims['id']
        
    # is customer_id valid?
    cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (data['customer_id'],))
    customer = cursor.fetchone()
    if not customer:
        db.close()
        return jsonify({"message": "Invalid customer_id: Customer does not exist"}), 400
    
    # is there room
    cursor.execute("SELECT * FROM rooms WHERE room_id = %s", (data['room_id'],))
    customer = cursor.fetchone()
    if not customer:
        db.close()
        return jsonify({"message": "Invalid room_id: Room does not exist"}), 400
    
    # is room empty 
    cursor.execute("""
        SELECT * FROM reservations
        WHERE room_id = %s
        AND (
            (check_in_date <= %s AND check_out_date > %s) OR
            (check_in_date < %s AND check_out_date >= %s) OR
            (check_in_date >= %s AND check_out_date <= %s)
        )
    """, (
        data['room_id'],
        data['check_in_date'], data['check_in_date'],
        data['check_out_date'], data['check_out_date'],
        data['check_in_date'], data['check_out_date']
    ))
    conflicting_reservation = cursor.fetchone()
    if conflicting_reservation:
        db.close()
        return jsonify({"message": "The room is already booked for the given dates"}), 400

    
    cursor.execute("INSERT INTO reservations (customer_id, check_in_date, check_out_date, room_id) VALUES (%s, %s, %s, %s)",
                   (data['customer_id'], data['check_in_date'], data['check_out_date'], data['room_id']))
    db.commit()
    db.close()
    return jsonify({"message": "Reservation added successfully!"}), 201
@reservations_bp.route('/<int:reservation_id>', methods=['PUT'])
@jwt_required()
def update_reservation(reservation_id):
    claims = get_jwt()
    current_user = get_jwt_identity()
    data = request.json

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    if claims['role'] != 'admin':
        data['customer_id'] = claims['id']
    # Güncellenen rezervasyonun var olup olmadığını kontrol et
    cursor.execute("SELECT * FROM reservations WHERE reservation_id = %s", (reservation_id,))
    reservation = cursor.fetchone()
    if not reservation:
        db.close()
        return jsonify({"message": "Invalid reservation_id: Reservation does not exist"}), 400
    

    # customer_id'nin geçerli olup olmadığını kontrol et
    cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (data['customer_id'],))
    customer = cursor.fetchone()
    if not customer:
        db.close()
        return jsonify({"message": "Invalid customer_id: Customer does not exist"}), 400

    # Tarih çakışmasını kontrol et (mevcut rezervasyon hariç)
    cursor.execute("""
        SELECT * FROM reservations
        WHERE room_id = %s
        AND reservation_id != %s
        AND (
            (check_in_date <= %s AND check_out_date > %s) OR
            (check_in_date < %s AND check_out_date >= %s) OR
            (check_in_date >= %s AND check_out_date <= %s)
        )
    """, (
        data['room_id'], reservation_id,
        data['check_in_date'], data['check_in_date'],
        data['check_out_date'], data['check_out_date'],
        data['check_in_date'], data['check_out_date']
    ))
    conflicting_reservation = cursor.fetchone()
    if conflicting_reservation:
        db.close()
        return jsonify({"message": "The room is already booked for the given dates"}), 400

    # Güncellemeyi yap
    cursor.execute(
        "UPDATE reservations SET customer_id = %s, check_in_date = %s, check_out_date = %s, room_id = %s WHERE reservation_id = %s",
        (data['customer_id'], data['check_in_date'], data['check_out_date'], data['room_id'], reservation_id)
    )
    db.commit()
    db.close()

    return jsonify({"message": "Reservation updated successfully!"})


@reservations_bp.route('/<int:reservation_id>', methods=['DELETE'])
@jwt_required()
def delete_reservation(reservation_id):
    claims = get_jwt()
    current_user = get_jwt_identity()

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Silinmek istenen rezervasyonun varlığını kontrol et
    cursor.execute("SELECT * FROM reservations WHERE reservation_id = %s", (reservation_id,))
    reservation = cursor.fetchone()
    if not reservation:
        db.close()
        return jsonify({"message": "Invalid reservation_id: Reservation does not exist"}), 400

    # Admin olmayan kullanıcıların kendi rezervasyonunu silmesi için kontrol
    if claims['role'] != 'admin' and claims['id'] != reservation['customer_id']:
        db.close()
        return jsonify({"message": "You are not authorized to delete this reservation"}), 403

    # Rezervasyonu sil
    cursor.execute("DELETE FROM reservations WHERE reservation_id = %s", (reservation_id,))
    db.commit()
    db.close()

    return jsonify({"message": "Reservation deleted successfully!"})
