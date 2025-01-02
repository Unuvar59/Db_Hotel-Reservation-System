from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import get_db_connection
from flask_restx import Namespace, Resource, fields

payments_bp = Blueprint('payments', __name__)

# Swagger Namespace
api = Namespace('Payments', description='Operations related to payments')

# Swagger Models
payment_model = api.model('Payment', {
    'reservation_id': fields.Integer(required=True, description='Reservation ID'),
    'amount': fields.Float(required=True, description='Payment amount'),
    'payment_date': fields.String(required=True, description='Payment date (YYYY-MM-DD)')
})

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
                # Kullanıcı yalnızca kendi ödemelerini görebilir
                current_user_id = claims['id']
                cursor.execute("""
                    SELECT payments.* FROM payments
                    JOIN reservations ON payments.reservation_id = reservations.reservation_id
                    WHERE reservations.customer_id = %s
                """, (current_user_id,))
                payments = cursor.fetchall()
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

            # Kullanıcı yalnızca kendi rezervasyonları için ödeme yapabilir
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
            # Ödeme bilgilerini al
            cursor.execute("SELECT * FROM payments WHERE payment_id = %s", (payment_id,))
            payment = cursor.fetchone()
            if not payment:
                db.close()
                return {"message": "Invalid payment_id: Payment does not exist"}, 400

            # Rezervasyonun bilgilerini kontrol et
            cursor.execute("""
                SELECT * FROM reservations WHERE reservation_id = %s
            """, (payment['reservation_id'],))
            reservation = cursor.fetchone()
            if not reservation:
                db.close()
                return {"message": "Invalid reservation associated with this payment"}, 400

            # Admin olmayan kullanıcılar yalnızca kendi rezervasyonlarına ait ödemeleri silebilir
            if claims['role'] != 'admin' and reservation['customer_id'] != claims['id']:
                db.close()
                return {"message": "You are not authorized to delete this payment"}, 403

            # Ödemeyi sil
            cursor.execute("DELETE FROM payments WHERE payment_id = %s", (payment_id,))
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error deleting payment", "error": str(e)}, 500
        db.close()
        return {"message": "Payment deleted successfully!"}, 200
