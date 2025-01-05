from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import get_db_connection
from datetime import date, datetime
from flask_restx import Namespace, Resource, fields
from decimal import Decimal

feedback_bp = Blueprint('feedback', __name__)

# Swagger Namespace
api = Namespace('Feedback', description='Operations related to feedback')

# Swagger Models
feedback_model = api.model('Feedback', {
    'customer_id': fields.Integer(required=True, description='Customer ID'),
    'feedback_details': fields.String(required=True, description='Details of the feedback'),
    'feedback_date': fields.String(description='Date of the feedback (optional, defaults to today)')
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
class FeedbackList(Resource):
    @api.doc('list_feedback', responses={
        200: 'Success',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def get(self):
        """List all feedback"""
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM feedback")
            feedback = cursor.fetchall()
            # Serialize non-serializable data
            feedback = serialize_data(feedback)
        except Exception as e:
            db.close()
            return {"message": "Error retrieving feedback", "error": str(e)}, 500
        db.close()
        return feedback, 200

    @api.expect(feedback_model)
    @api.doc('add_feedback', responses={
        201: 'Feedback added successfully!',
        400: 'Invalid customer_id',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def post(self):
        """Add new feedback"""
        claims = get_jwt()
        data = request.json
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:
            # Check if customer_id exists
            cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (data['customer_id'],))
            customer = cursor.fetchone()
            if not customer:
                db.close()
                return {"message": "Invalid customer_id: Customer does not exist"}, 400

            # non-admin user control
            if claims['role'] != 'admin' and (customer['customer_id'] != claims['id'] or data['customer_id'] != claims['id']):
                db.close()
                return {"message": "You are not authorized to add this feedback"}, 403

            # Get current date
            feedback_date = datetime.now().strftime('%Y-%m-%d')

            cursor.execute("INSERT INTO feedback (customer_id, feedback_details, feedback_date) VALUES (%s, %s, %s)",
                           (data['customer_id'], data['feedback_details'], feedback_date))
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error adding feedback", "error": str(e)}, 500
        db.close()
        return {"message": "Feedback added successfully!"}, 201

@api.route('/<int:feedback_id>')
class Feedback(Resource):
    @api.expect(feedback_model)
    @api.doc('update_feedback', responses={
        200: 'Feedback updated successfully!',
        400: 'Invalid feedback_id or customer_id',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def put(self, feedback_id):
        """Update existing feedback"""
        claims = get_jwt()
        data = request.json
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:
            # Check if feedback exists
            cursor.execute("SELECT * FROM feedback WHERE feedback_id = %s", (feedback_id,))
            feedback = cursor.fetchone()
            if not feedback:
                db.close()
                return {"message": "Invalid feedback_id: Feedback does not exist"}, 400

            # Check if customer_id exists
            cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (data['customer_id'],))
            customer = cursor.fetchone()
            if not customer:
                db.close()
                return {"message": "Invalid customer_id: Customer does not exist"}, 400

            # non-admin user control
            if claims['role'] != 'admin' and (customer['customer_id'] != claims['id'] or data['customer_id'] != claims['id']):
                db.close()
                return {"message": "You are not authorized to update this feedback"}, 403

            cursor.execute("UPDATE feedback SET customer_id = %s, feedback_details = %s, feedback_date = %s WHERE feedback_id = %s",
                           (data['customer_id'], data['feedback_details'], data.get('feedback_date', datetime.now().strftime('%Y-%m-%d')), feedback_id))
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error updating feedback", "error": str(e)}, 500
        db.close()
        return {"message": "Feedback updated successfully!"}, 200

    @api.doc('delete_feedback', responses={
        200: 'Feedback deleted successfully!',
        400: 'Invalid feedback_id',
        403: 'Access Denied',
        500: 'Internal Server Error'
    })
    @jwt_required()
    def delete(self, feedback_id):
        """Delete feedback"""
        claims = get_jwt()
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:
            # Check if feedback exists
            cursor.execute("SELECT * FROM feedback WHERE feedback_id = %s", (feedback_id,))
            feedback = cursor.fetchone()
            if not feedback:
                db.close()
                return {"message": "Invalid feedback_id: Feedback does not exist"}, 400

            # non-admin user control
            if claims['role'] != 'admin' and feedback['customer_id'] != claims['id']:
                db.close()
                return {"message": "You are not authorized to delete this feedback"}, 403

            # Delete feedback
            cursor.execute("DELETE FROM feedback WHERE feedback_id = %s", (feedback_id,))
            db.commit()
        except Exception as e:
            db.close()
            return {"message": "Error deleting feedback", "error": str(e)}, 500
        db.close()
        return {"message": "Feedback deleted successfully!"}, 200
