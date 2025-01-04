from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import get_db_connection
from flask_restx import Namespace, Resource, fields
from decimal import Decimal
from datetime import date, datetime

roomservices_bp = Blueprint('roomservices', __name__)

# Swagger Namespace
api = Namespace('RoomServices', description='Operations related to room services')

# Swagger Model
roomservice_model = api.model('RoomService', {
    'room_id': fields.Integer(required=True, description='Room ID'),
    'service_type': fields.String(required=True, description='Type of the service'),
    'cost': fields.Float(required=True, description='Cost of the service')
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
class RoomServiceList(Resource):
    @api.doc('list_roomservices', responses={
        200: 'Success',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def get(self):
        """List all room services (Admin only)"""
        claims = get_jwt()
        if claims['role'] != 'admin':
            return {"message": "Access denied"}, 403

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM roomservices")
            roomservices = cursor.fetchall()
            roomservices = serialize_data(roomservices) # convert data to JSON serializable types
        except Exception as e:
            db.close()
            return {"message": "Error retrieving room services", "error": str(e)}, 500
        db.close()
        return roomservices, 200

    @api.expect(roomservice_model)
    @api.doc('add_roomservice', responses={
        201: 'Room service added successfully!',
        400: 'Invalid room_id',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def post(self):
        """Add a new room service (Admin only)"""
        claims = get_jwt()
        if claims['role'] != 'admin':
            return {"message": "Access denied"}, 403

        data = request.json
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Check if room_id exists
        cursor.execute("SELECT * FROM rooms WHERE room_id = %s", (data['room_id'],))
        room = cursor.fetchone()
        if not room:
            db.close()
            return {"message": "Invalid room_id: Room does not exist"}, 400

        try:
            cursor.execute("INSERT INTO roomservices (room_id, service_type, cost) VALUES (%s, %s, %s)",
                           (data['room_id'], data['service_type'], data['cost']))
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error adding room service", "error": str(e)}, 500
        db.close()
        return {"message": "Room service added successfully!"}, 201

@api.route('/<int:service_id>')
class RoomService(Resource):
    @api.doc('update_roomservice', responses={
        200: 'Room service updated successfully!',
        400: 'Invalid room_id',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @api.expect(roomservice_model)
    @jwt_required()
    def put(self, service_id):
        """Update a room service (Admin only)"""
        claims = get_jwt()
        if claims['role'] != 'admin':
            return {"message": "Access denied"}, 403

        data = request.json
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Check if room_id exists
        cursor.execute("SELECT * FROM rooms WHERE room_id = %s", (data['room_id'],))
        room = cursor.fetchone()
        if not room:
            db.close()
            return {"message": "Invalid room_id: Room does not exist"}, 400

        try:
            cursor.execute("UPDATE roomservices SET room_id = %s, service_type = %s, cost = %s WHERE service_id = %s",
                           (data['room_id'], data['service_type'], data['cost'], service_id))
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error updating room service", "error": str(e)}, 500
        db.close()
        return {"message": "Room service updated successfully!"}, 200

    @api.doc('delete_roomservice', responses={
        200: 'Room service deleted successfully!',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def delete(self, service_id):
        """Delete a room service (Admin only)"""
        claims = get_jwt()
        if claims['role'] != 'admin':
            return {"message": "Access denied"}, 403

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("DELETE FROM roomservices WHERE service_id = %s", (service_id,))
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error deleting room service", "error": str(e)}, 500
        db.close()
        return {"message": "Room service deleted successfully!"}, 200