from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import get_db_connection
from flask_restx import Api, Resource, fields, Namespace
from datetime import date, datetime
from decimal import Decimal

customerevents_bp = Blueprint('customerevents', __name__)

# Swagger namespace
api = Namespace('CustomerEvents', description='Operations related to customer events')

# Swagger model
customerevent_model = api.model('CustomerEvent', {
    'customer_id': fields.Integer(required=True, description='ID of the customer'),
    'event_id': fields.Integer(required=True, description='ID of the event'),
    'participation_date': fields.String(required=True, description='Date of participation (YYYY-MM-DD)')
})

def serialize_dates(data):
    """Convert datetime.date or datetime.datetime objects to JSON serializable string."""
    if isinstance(data, list):
        return [
            {
                key: value.strftime('%Y-%m-%d') if isinstance(value, (date, datetime)) else value
                for key, value in item.items()
            }
            for item in data
        ]
    elif isinstance(data, dict):
        return {
            key: value.strftime('%Y-%m-%d') if isinstance(value, (date, datetime)) else value
            for key, value in data.items()
        }
    return data

@api.route('/')
class CustomerEventList(Resource):
    @api.doc('list_customerevents', responses={
        200: 'Success',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def get(self):
        """List all customer events"""
        claims = get_jwt()
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:
            if claims['role'] == 'admin':
                cursor.execute("SELECT * FROM customerevents")
            else:
                cursor.execute("SELECT * FROM customerevents WHERE customer_id = %s", (claims['id'],))
            customerevents = cursor.fetchall()

            # Serialize dates to JSON serializable format
            customerevents = serialize_dates(customerevents)

        except Exception as e:
            db.close()
            return {"message": "Error retrieving customer events", "error": str(e)}, 500
        db.close()
        return customerevents, 200

    @api.expect(customerevent_model)
    @api.doc('add_customerevent', responses={
        201: 'Customer event added successfully!',
        400: 'Invalid customer_id or event_id',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def post(self):
        """Add a new customer event"""
        claims = get_jwt()
        data = request.json

        if claims['role'] != 'admin' and data['customer_id'] != claims['id']:
            return {"message": "You are not authorized to add this customer event"}, 403

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:
            # Check customer existence
            cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (data['customer_id'],))
            if not cursor.fetchone():
                db.close()
                return {"message": "Invalid customer_id: Customer does not exist"}, 400

            # Check event existence
            cursor.execute("SELECT * FROM events WHERE event_id = %s", (data['event_id'],))
            event = cursor.fetchone()
            if not event:
                db.close()
                return {"message": "Invalid event_id: Event does not exist"}, 400

            # Check participation date
            if data['participation_date'] != event['date'].strftime('%Y-%m-%d'):
                db.close()
                return {"message": "Participation date must match the event date"}, 400

            # Insert the customer event
            cursor.execute(
                "INSERT INTO customerevents (customer_id, event_id, participation_date) VALUES (%s, %s, %s)",
                (data['customer_id'], data['event_id'], data['participation_date'])
            )
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error adding customer event", "error": str(e)}, 500
        db.close()
        return {"message": "Customer event added successfully!"}, 201

@api.route('/<int:customerevent_id>')
class CustomerEvent(Resource):
    @api.doc('get_customerevent', responses={
        200: 'Success',
        403: 'Access Denied',
        404: 'Customer event not found',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def get(self, customerevent_id):
        """Get a specific customer event"""
        claims = get_jwt()
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM customerevents WHERE customerevent_id = %s", (customerevent_id,))
            customerevent = cursor.fetchone()
            if not customerevent:
                db.close()
                return {"message": "Customer event not found"}, 404

            if claims['role'] != 'admin' and customerevent['customer_id'] != claims['id']:
                db.close()
                return {"message": "Access denied"}, 403
            
            # convert dates to JSON serializable format
            customerevent = serialize_dates(customerevent)

        except Exception as e:
            db.close()
            return {"message": "Error retrieving customer event", "error": str(e)}, 500

        db.close()
        return customerevent, 200

    @api.expect(customerevent_model)
    @api.doc('update_customerevent', responses={
        200: 'Customer event updated successfully!',
        400: 'Invalid customer_id or event_id',
        403: 'Access Denied',
        404: 'Customer event not found',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def put(self, customerevent_id):
        """Update a customer event"""
        claims = get_jwt()
        data = request.json
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM customerevents WHERE customerevent_id = %s", (customerevent_id,))
            customerevent = cursor.fetchone()
            if not customerevent:
                db.close()
                return {"message": "Customer event not found"}, 404

            if claims['role'] != 'admin' and customerevent['customer_id'] != claims['id']:
                db.close()
                return {"message": "Access denied"}, 403

            # Check customer existence
            cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (data['customer_id'],))
            if not cursor.fetchone():
                db.close()
                return {"message": "Invalid customer_id: Customer does not exist"}, 400

            # Check event existence
            cursor.execute("SELECT * FROM events WHERE event_id = %s", (data['event_id'],))
            event = cursor.fetchone()
            if not event:
                db.close()
                return {"message": "Invalid event_id: Event does not exist"}, 400

            # Check participation date
            if data['participation_date'] != str(event['date']):
                db.close()
                return {"message": "Participation date must match the event date"}, 400

            # Update the customer event
            cursor.execute(
                "UPDATE customerevents SET customer_id = %s, event_id = %s, participation_date = %s WHERE customerevent_id = %s",
                (data['customer_id'], data['event_id'], data['participation_date'], customerevent_id)
            )
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error updating customer event", "error": str(e)}, 500

        db.close()
        return {"message": "Customer event updated successfully!"}, 200

    @api.doc('delete_customerevent', responses={
        200: 'Customer event deleted successfully!',
        403: 'Access Denied',
        404: 'Customer event not found',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def delete(self, customerevent_id):
        """Delete a customer event"""
        claims = get_jwt()
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM customerevents WHERE customerevent_id = %s", (customerevent_id,))
            customerevent = cursor.fetchone()
            if not customerevent:
                db.close()
                return {"message": "Customer event not found"}, 404

            if claims['role'] != 'admin' and customerevent['customer_id'] != claims['id']:
                db.close()
                return {"message": "Access denied"}, 403

            # Delete the customer event
            cursor.execute("DELETE FROM customerevents WHERE customerevent_id = %s", (customerevent_id,))
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error deleting customer event", "error": str(e)}, 500

        db.close()
        return {"message": "Customer event deleted successfully!"}, 200

