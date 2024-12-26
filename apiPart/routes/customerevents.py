from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import get_db_connection

customerevents_bp = Blueprint('customerevents', __name__)

@customerevents_bp.route('/', methods=['GET'])
@jwt_required()
def get_customerevents():
    claims = get_jwt()
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if claims['role'] == 'admin':
        # Admin tüm etkinlikleri görebilir
        cursor.execute("SELECT * FROM customerevents")
    else:
        # Kullanıcı yalnızca kendi etkinliklerini görebilir
        cursor.execute("SELECT * FROM customerevents WHERE customer_id = %s", (claims['id'],))

    customerevents = cursor.fetchall()
    db.close()
    return jsonify(customerevents)

@customerevents_bp.route('/', methods=['POST'])
@jwt_required()
def add_customerevent():
    claims = get_jwt()
    data = request.json

    # Kullanıcı yalnızca kendi customer_id'siyle etkinlik ekleyebilir
    if claims['role'] != 'admin' and data['customer_id'] != claims['id']:
        return jsonify({"message": "You are not authorized to add this customer event"}), 403

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Etkinlik ekle
    cursor.execute(
        "INSERT INTO customerevents (customer_id, event_id, participation_date) VALUES (%s, %s, %s)",
        (data['customer_id'], data['event_id'], data['participation_date'])
    )
    db.commit()
    db.close()
    return jsonify({"message": "Customer event added successfully!"}), 201

@customerevents_bp.route('/<int:customerevent_id>', methods=['PUT'])
@jwt_required()
def update_customerevent(customerevent_id):
    claims = get_jwt()
    data = request.json
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Güncellenecek etkinliğin varlığını kontrol et
    cursor.execute("SELECT * FROM customerevents WHERE customerevent_id = %s", (customerevent_id,))
    customerevent = cursor.fetchone()
    if not customerevent:
        db.close()
        return jsonify({"message": "Invalid customerevent_id: Customer event does not exist"}), 400

    # Admin olmayan kullanıcılar yalnızca kendi etkinliklerini güncelleyebilir
    if claims['role'] != 'admin' and customerevent['customer_id'] != claims['id']:
        db.close()
        return jsonify({"message": "You are not authorized to update this customer event"}), 403

    # Etkinliği güncelle
    cursor.execute(
        "UPDATE customerevents SET customer_id = %s, event_id = %s, participation_date = %s WHERE customerevent_id = %s",
        (data['customer_id'], data['event_id'], data['participation_date'], customerevent_id)
    )
    db.commit()
    db.close()
    return jsonify({"message": "Customer event updated successfully!"})

@customerevents_bp.route('/<int:customerevent_id>', methods=['DELETE'])
@jwt_required()
def delete_customerevent(customerevent_id):
    claims = get_jwt()
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Silinecek etkinliğin varlığını kontrol et
    cursor.execute("SELECT * FROM customerevents WHERE customerevent_id = %s", (customerevent_id,))
    customerevent = cursor.fetchone()
    if not customerevent:
        db.close()
        return jsonify({"message": "Invalid customerevent_id: Customer event does not exist"}), 400

    # Admin olmayan kullanıcılar yalnızca kendi etkinliklerini silebilir
    if claims['role'] != 'admin' and customerevent['customer_id'] != claims['id']:
        db.close()
        return jsonify({"message": "You are not authorized to delete this customer event"}), 403

    # Etkinliği sil
    cursor.execute("DELETE FROM customerevents WHERE customerevent_id = %s", (customerevent_id,))
    db.commit()
    db.close()
    return jsonify({"message": "Customer event deleted successfully!"})
