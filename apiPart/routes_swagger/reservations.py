from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import get_db_connection
from flask_restx import Namespace, Resource, fields

reservations_bp = Blueprint('reservations', __name__)

# Swagger Namespace
api = Namespace('Reservations', description='Operations related to reservations')

# Swagger Models
reservation_model = api.model('Reservation', {
    'customer_id': fields.Integer(description='Customer ID (only for admin users)'),
    'room_id': fields.Integer(required=True, description='Room ID'),
    'check_in_date': fields.String(required=True, description='Check-in date (YYYY-MM-DD)'),
    'check_out_date': fields.String(required=True, description='Check-out date (YYYY-MM-DD)')
})

@api.route('/')
class ReservationList(Resource):
    @api.doc('list_reservations', responses={
        200: 'Success',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def get(self):
        """List all reservations (Admin only)"""
        claims = get_jwt()
        if claims['role'] != 'admin':
            return {"message": "Access denied"}, 403

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM reservations")
            reservations = cursor.fetchall()

            # convert datetime objects to string
            for reservation in reservations:
                if 'check_in_date' in reservation:
                    reservation['check_in_date'] = reservation['check_in_date'].strftime('%Y-%m-%d')
                if 'check_out_date' in reservation:
                    reservation['check_out_date'] = reservation['check_out_date'].strftime('%Y-%m-%d')
        
        except Exception as e:
            db.close()
            return {"message": "Error retrieving reservations", "error": str(e)}, 500
        db.close()
        return reservations, 200

    @api.expect(reservation_model)
    @api.doc('add_reservation', responses={
        201: 'Reservation added successfully!',
        400: 'Invalid customer_id or room_id, or room is already booked',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def post(self):
        """Add a new reservation"""
        claims = get_jwt()
        current_user = get_jwt_identity()
        data = request.json
        if claims['role'] != 'admin':
            data['customer_id'] = claims['id']

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:
            # Check if customer_id is valid
            cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (data['customer_id'],))
            customer = cursor.fetchone()
            if not customer:
                db.close()
                return {"message": "Invalid customer_id: Customer does not exist"}, 400

            # Check if room_id is valid
            cursor.execute("SELECT * FROM rooms WHERE room_id = %s", (data['room_id'],))
            room = cursor.fetchone()
            if not room:
                db.close()
                return {"message": "Invalid room_id: Room does not exist"}, 400

            # Check if room is available
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
                return {"message": "The room is already booked for the given dates"}, 400

            # Insert reservation
            cursor.execute("""
                INSERT INTO reservations (customer_id, check_in_date, check_out_date, room_id)
                VALUES (%s, %s, %s, %s)
            """, (data['customer_id'], data['check_in_date'], data['check_out_date'], data['room_id']))
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error adding reservation", "error": str(e)}, 500
        db.close()
        return {"message": "Reservation added successfully!"}, 201

@api.route('/<int:reservation_id>')
class Reservation(Resource):
    @api.expect(reservation_model)
    @api.doc('update_reservation', responses={
        200: 'Reservation updated successfully!',
        400: 'Invalid reservation_id, customer_id, or room_id, or room is already booked',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def put(self, reservation_id):
        """Update a reservation"""
        claims = get_jwt()
        data = request.json
        if claims['role'] != 'admin':
            data['customer_id'] = claims['id']

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:
            # Check if reservation exists
            cursor.execute("SELECT * FROM reservations WHERE reservation_id = %s", (reservation_id,))
            reservation = cursor.fetchone()
            if not reservation:
                db.close()
                return {"message": "Invalid reservation_id: Reservation does not exist"}, 400

            # Check if room is available
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
                return {"message": "The room is already booked for the given dates"}, 400

            # Update reservation
            cursor.execute("""
                UPDATE reservations SET customer_id = %s, check_in_date = %s, check_out_date = %s, room_id = %s
                WHERE reservation_id = %s
            """, (data['customer_id'], data['check_in_date'], data['check_out_date'], data['room_id'], reservation_id))
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error updating reservation", "error": str(e)}, 500
        db.close()
        return {"message": "Reservation updated successfully!"}, 200

    @api.doc('delete_reservation', responses={
        200: 'Reservation deleted successfully!',
        400: 'Invalid reservation_id',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def delete(self, reservation_id):
        """Delete a reservation"""
        claims = get_jwt()

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:
            # Check if reservation exists
            cursor.execute("SELECT * FROM reservations WHERE reservation_id = %s", (reservation_id,))
            reservation = cursor.fetchone()
            if not reservation:
                db.close()
                return {"message": "Invalid reservation_id: Reservation does not exist"}, 400

            # non-admin users can only delete their own reservations
            if claims['role'] != 'admin' and claims['id'] != reservation['customer_id']:
                db.close()
                return {"message": "You are not authorized to delete this reservation"}, 403

            # Delete reservation
            cursor.execute("DELETE FROM reservations WHERE reservation_id = %s", (reservation_id,))
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error deleting reservation", "error": str(e)}, 500
        db.close()
        return {"message": "Reservation deleted successfully!"}, 200
