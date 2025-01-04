from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import get_db_connection
from flask_restx import Namespace, Resource, fields
from datetime import date, datetime
from decimal import Decimal

events_bp = Blueprint('events', __name__)

# Swagger Namespace
api = Namespace('Events', description='Operations related to events')

# Swagger Models
event_model = api.model('Event', {
    'event_name': fields.String(required=True, description='Name of the event'),
    'date': fields.String(required=True, description='Date of the event (YYYY-MM-DD)'),
    'participation_fee': fields.Float(required=True, description='Participation fee for the event')
})

# Helper function to serialize dates and decimals
def serialize_dates_and_decimals(data):
    """Convert date, datetime, and Decimal objects to JSON serializable types."""
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
class EventList(Resource):
    @api.doc('list_events', responses={
        200: 'Success',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def get(self):
        """List all events"""
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM events")
            events = cursor.fetchall()
            # Serialize dates for JSON compatibility
            events = serialize_dates_and_decimals(events)
        except Exception as e:
            db.close()
            return {"message": "Error retrieving events", "error": str(e)}, 500
        db.close()
        return events, 200

    @api.expect(event_model)
    @api.doc('add_event', responses={
        201: 'Event added successfully!',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def post(self):
        """Add a new event (Admin only)"""
        claims = get_jwt()
        if claims['role'] != 'admin':
            return {"message": "Access denied"}, 403

        data = request.json
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("INSERT INTO events (event_name, date, participation_fee) VALUES (%s, %s, %s)",
                           (data['event_name'], data['date'], data['participation_fee']))
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error adding event", "error": str(e)}, 500
        db.close()
        return {"message": "Event added successfully!"}, 201

@api.route('/<int:event_id>')
class Event(Resource):
    @api.expect(event_model)
    @api.doc('update_event', responses={
        200: 'Event updated successfully!',
        400: 'Invalid event_id',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def put(self, event_id):
        """Update an event (Admin only)"""
        claims = get_jwt()
        if claims['role'] != 'admin':
            return {"message": "Access denied"}, 403

        data = request.json
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:
            # Check if event_id exists
            cursor.execute("SELECT * FROM events WHERE event_id = %s", (event_id,))
            event = cursor.fetchone()
            if not event:
                db.close()
                return {"message": "Invalid event_id: Event does not exist"}, 400

            cursor.execute("UPDATE events SET event_name = %s, date = %s, participation_fee = %s WHERE event_id = %s",
                           (data['event_name'], data['date'], data['participation_fee'], event_id))
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error updating event", "error": str(e)}, 500
        db.close()
        return {"message": "Event updated successfully!"}, 200

    @api.doc('delete_event', responses={
        200: 'Event deleted successfully!',
        400: 'Invalid event_id',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def delete(self, event_id):
        """Delete an event (Admin only)"""
        claims = get_jwt()
        if claims['role'] != 'admin':
            return {"message": "Access denied"}, 403

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:
            # Check if event_id exists
            cursor.execute("SELECT * FROM events WHERE event_id = %s", (event_id,))
            event = cursor.fetchone()
            if not event:
                db.close()
                return {"message": "Invalid event_id: Event does not exist"}, 400

            cursor.execute("DELETE FROM events WHERE event_id = %s", (event_id,))
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error deleting event", "error": str(e)}, 500
        db.close()
        return {"message": "Event deleted successfully!"}, 200