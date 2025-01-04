from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import get_db_connection
from flask_restx import Namespace, Resource, fields
from decimal import Decimal
from datetime import date, datetime

rooms_bp = Blueprint('rooms', __name__)

# Swagger Namespace
api = Namespace('Rooms', description='Operations related to rooms')

# Swagger Model
room_model = api.model('Room', {
    'type': fields.String(required=True, description='Type of the room'),
    'pricing': fields.Float(required=True, description='Pricing of the room'),
    'capacity': fields.Integer(required=True, description='Capacity of the room')
})

def serialize_data(data):
    """Convert non-serializable objects to JSON serializable types."""
    if isinstance(data, list):
        return [
            {
                key: (
                    value.strftime('%Y-%m-%d') if isinstance(value, (date, datetime)) else
                    float(value) if isinstance(value, Decimal) else
                    value
                )
                for key, value in item.items()
            }
            for item in data
        ]
    elif isinstance(data, dict):
        return {
            key: (
                value.strftime('%Y-%m-%d') if isinstance(value, (date, datetime)) else
                float(value) if isinstance(value, Decimal) else
                value
            )
            for key, value in data.items()
        }
    return data

@api.route('/')
class RoomList(Resource):
    @api.doc('list_rooms', responses={
        200: 'Success',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def get(self):
        """List all rooms"""
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM rooms")
            rooms = cursor.fetchall()
            rooms = serialize_data(rooms) # convert data to JSON serializable types
        except Exception as e:
            db.close()
            return {"message": "Error retrieving rooms", "error": str(e)}, 500
        db.close()
        return rooms, 200

    @api.expect(room_model)
    @api.doc('add_room', responses={
        201: 'Room added successfully!',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def post(self):
        """Add a new room"""
        claims = get_jwt()
        if claims['role'] != 'admin':
            return {"message": "Access denied"}, 403

        data = request.json
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("INSERT INTO rooms (type, pricing, capacity) VALUES (%s, %s, %s)",
                           (data['type'], data['pricing'], data['capacity']))
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error adding room", "error": str(e)}, 500
        db.close()
        return {"message": "Room added successfully!"}, 201

@api.route('/<int:room_id>')
class Room(Resource):
    @api.doc('update_room', responses={
        200: 'Room updated successfully!',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @api.expect(room_model)
    @jwt_required()
    def put(self, room_id):
        """Update a room"""
        claims = get_jwt()
        if claims['role'] != 'admin':
            return {"message": "Access denied"}, 403

        data = request.json
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("UPDATE rooms SET type = %s, pricing = %s, capacity = %s WHERE room_id = %s",
                           (data['type'], data['pricing'], data['capacity'], room_id))
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error updating room", "error": str(e)}, 500
        db.close()
        return {"message": "Room updated successfully!"}, 200

    @api.doc('delete_room', responses={
        200: 'Room deleted successfully!',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def delete(self, room_id):
        """Delete a room"""
        claims = get_jwt()
        if claims['role'] != 'admin':
            return {"message": "Access denied"}, 403

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("DELETE FROM rooms WHERE room_id = %s", (room_id,))
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error deleting room", "error": str(e)}, 500
        db.close()
        return {"message": "Room deleted successfully!"}, 200