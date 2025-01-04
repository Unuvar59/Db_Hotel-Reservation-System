from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import get_db_connection
from flask_restx import Namespace, Resource, fields
from decimal import Decimal
from datetime import date

payments_bp = Blueprint('payments', __name__)

# Swagger Namespace
api = Namespace('Payments', description='Operations related to payments')

# Swagger Models
payment_model = api.model('Payment', {
    'reservation_id': fields.Integer(required=True, description='Reservation ID'),
    'amount': fields.Float(required=True, description='Payment amount'),
    'payment_date': fields.String(required=True, description='Payment date (YYYY-MM-DD)')
})

def serialize_data(data):
    """Convert Decimal and date values in a list or dictionary to JSON-serializable types."""
    if isinstance(data, list):
        for item in data:
            for key, value in item.items():
                if isinstance(value, Decimal):
                    item[key] = float(value)
                elif isinstance(value, date):
                    item[key] = value.strftime('%Y-%m-%d')
    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, Decimal):
                data[key] = float(value)
            elif isinstance(value, date):
                data[key] = value.strftime('%Y-%m-%d')
    return data

@api.route('/')
class PaymentList(Resource):
    @api.doc('list_payments', responses={
        200: 'Success',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def get(self):
        """List all payments (Admin: all, User: own payments)"""
        claims = get_jwt()
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:
            if claims['role'] == 'admin':
                cursor.execute("SELECT * FROM payments")
                payments = cursor.fetchall()
            else:
                # user can only see their own payments
                current_user_id = claims['id']
                cursor.execute("""
                    SELECT payments.* FROM payments
                    JOIN reservations ON payments.reservation_id = reservations.reservation_id
                    WHERE reservations.customer_id = %s
                """, (current_user_id,))
                payments = cursor.fetchall()

            # convert Decimal and date values to JSON-serializable types
            payments = serialize_data(payments)

        except Exception as e:
            db.close()
            return {"message": "Error retrieving payments", "error": str(e)}, 500
        db.close()
        return payments, 200

    @api.expect(payment_model)
    @api.doc('add_payment', responses={
        201: 'Payment added successfully!',
        400: 'Invalid reservation_id',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def post(self):
        """Add a new payment"""
        claims = get_jwt()
        data = request.json
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:
            # Check if reservation exists
            cursor.execute("SELECT * FROM reservations WHERE reservation_id = %s", (data['reservation_id'],))
            reservation = cursor.fetchone()
            if not reservation:
                db.close()
                return {"message": "Invalid reservation_id: Reservation does not exist"}, 400

            # users can only add payments for their own reservations
            if claims['role'] != 'admin' and reservation['customer_id'] != claims['id']:
                db.close()
                return {"message": "You are not authorized to add payment for this reservation"}, 403

            cursor.execute(
                "INSERT INTO payments (reservation_id, amount, payment_date) VALUES (%s, %s, %s)",
                (data['reservation_id'], data['amount'], data['payment_date'])
            )
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error adding payment", "error": str(e)}, 500
        db.close()
        return {"message": "Payment added successfully!"}, 201

@api.route('/<int:payment_id>')
class Payment(Resource):
    @api.doc('delete_payment', responses={
        200: 'Payment deleted successfully!',
        400: 'Invalid payment_id or reservation',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def delete(self, payment_id):
        """Delete a payment"""
        claims = get_jwt()
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:
            # get payment details
            cursor.execute("SELECT * FROM payments WHERE payment_id = %s", (payment_id,))
            payment = cursor.fetchone()
            if not payment:
                db.close()
                return {"message": "Invalid payment_id: Payment does not exist"}, 400

            # check if reservation exists
            cursor.execute("""
                SELECT * FROM reservations WHERE reservation_id = %s
            """, (payment['reservation_id'],))
            reservation = cursor.fetchone()
            if not reservation:
                db.close()
                return {"message": "Invalid reservation associated with this payment"}, 400

            # non-admin users can only delete their own payments
            if claims['role'] != 'admin' and reservation['customer_id'] != claims['id']:
                db.close()
                return {"message": "You are not authorized to delete this payment"}, 403

            # delete payment
            cursor.execute("DELETE FROM payments WHERE payment_id = %s", (payment_id,))
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error deleting payment", "error": str(e)}, 500
        db.close()
        return {"message": "Payment deleted successfully!"}, 200
