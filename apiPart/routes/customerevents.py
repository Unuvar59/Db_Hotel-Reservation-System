from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import get_db_connection
from flask_restx import Api, Resource, fields

customerevents_bp = Blueprint('customerevents', __name__)
api = Api(customerevents_bp, doc='/swagger', title="Customer Events API", description="API for managing customer events")

# Swagger model
customerevent_model = api.model('CustomerEvent', {
    'customer_id': fields.Integer(required=True, description='ID of the customer'),
    'event_id': fields.Integer(required=True, description='ID of the event'),
    'participation_date': fields.String(required=True, description='Date of participation (YYYY-MM-DD)')
})

@api.route('/')
class CustomerEventsList(Resource):
    @jwt_required()
    def get(self):
        """Get all customer events"""
        claims = get_jwt()
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        if claims['role'] == 'admin':
            # Admin can see all customerevents
            cursor.execute("SELECT * FROM customerevents")
        else:
            # Customer can only see their own customerevents
            cursor.execute("SELECT * FROM customerevents WHERE customer_id = %s", (claims['id'],))

        customerevents = cursor.fetchall()
        db.close()
        return jsonify(customerevents)

    @jwt_required()
    @api.expect(customerevent_model)
    def post(self):
        """Add a new customer event"""
        claims = get_jwt()
        data = request.json

        # Customer can only add their own customerevents
        if claims['role'] != 'admin' and data['customer_id'] != claims['id']:
            return jsonify({"message": "You are not authorized to add this customer event"}), 403

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # customer_id and event_id check when adding
        cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (data['customer_id'],))
        customer = cursor.fetchone()
        if not customer:
            db.close()
            return jsonify({"message": "Invalid customer_id: Customer does not exist"}), 400

        cursor.execute("SELECT * FROM events WHERE event_id = %s", (data['event_id'],))
        event = cursor.fetchone()
        if not event:
            db.close()
            return jsonify({"message": "Invalid event_id: Event does not exist"}), 400
        
        # check if participation date matches the event date
        if data['participation_date'] != str(event['date']):
            db.close()
            return jsonify({"message": "Participation date must match the event date"}), 400
        
        # add the customerevent
        cursor.execute(
            "INSERT INTO customerevents (customer_id, event_id, participation_date) VALUES (%s, %s, %s)",
            (data['customer_id'], data['event_id'], data['participation_date'])
        )
        db.commit()
        db.close()
        return jsonify({"message": "Customer event added successfully!"}), 201


@api.route('/<int:customerevent_id>')
class CustomerEvent(Resource):
    @jwt_required()
    def put(self, customerevent_id):
        """Update a customer event"""
        claims = get_jwt()
        data = request.json
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM customerevents WHERE customerevent_id = %s", (customerevent_id,))
        customerevent = cursor.fetchone()
        # a non-admin user can only update their own customerevents
        if claims['role'] != 'admin' and (customerevent['customer_id'] != claims['id'] or data['customer_id'] != claims['id']):
            db.close()
            return jsonify({"message": "You are not authorized to update this customer event"}), 403
        
        # check if the customerevent exists
        if not customerevent:
            db.close()
            return jsonify({"message": "Invalid customerevent_id: Customer event does not exist"}), 400

        # check if the customer and event exist when updating
        cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (data['customer_id'],))
        customer = cursor.fetchone()
        if not customer:
            db.close()
            return jsonify({"message": "Invalid customer_id: Customer does not exist"}), 400

        cursor.execute("SELECT * FROM events WHERE event_id = %s", (data['event_id'],))
        event = cursor.fetchone()
        if not event:
            db.close()
            return jsonify({"message": "Invalid event_id: Event does not exist"}), 400
        
        # check if participation date matches the event date
        if data['participation_date'] != str(event['date']):
            db.close()
            return jsonify({"message": "Participation date must match the event date"}), 400

        # update the customerevent
        cursor.execute(
            "UPDATE customerevents SET customer_id = %s, event_id = %s, participation_date = %s WHERE customerevent_id = %s",
            (data['customer_id'], data['event_id'], data['participation_date'], customerevent_id)
        )
        db.commit()
        db.close()
        return jsonify({"message": "Customer event updated successfully!"})

    @jwt_required()
    def delete(self, customerevent_id):
        """Delete a customer event"""
        claims = get_jwt()
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # check if the customerevent exists before deleting
        cursor.execute("SELECT * FROM customerevents WHERE customerevent_id = %s", (customerevent_id,))
        customerevent = cursor.fetchone()
        if not customerevent:
            db.close()
            return jsonify({"message": "Invalid customerevent_id: Customer event does not exist"}), 400

        # non-admin users can only delete their own customerevents
        if claims['role'] != 'admin' and customerevent['customer_id'] != claims['id']:
            db.close()
            return jsonify({"message": "You are not authorized to delete this customer event"}), 403

        # delete the customerevent
        cursor.execute("DELETE FROM customerevents WHERE customerevent_id = %s", (customerevent_id,))
        db.commit()
        db.close()
        return jsonify({"message": "Customer event deleted successfully!"})


# @customerevents_bp.route('/', methods=['GET'])
# @jwt_required()
# def get_customerevents():
#     claims = get_jwt()
#     db = get_db_connection()
#     cursor = db.cursor(dictionary=True)

#     if claims['role'] == 'admin':
#         # Admin can see all customerevents
#         cursor.execute("SELECT * FROM customerevents")
#     else:
#         # Customer can only see their own customerevents
#         cursor.execute("SELECT * FROM customerevents WHERE customer_id = %s", (claims['id'],))

#     customerevents = cursor.fetchall()
#     db.close()
#     return jsonify(customerevents)

# @customerevents_bp.route('/', methods=['POST'])
# @jwt_required()
# def add_customerevent():
#     claims = get_jwt()
#     data = request.json

#     # Customer can only add their own customerevents
#     if claims['role'] != 'admin' and data['customer_id'] != claims['id']:
#         return jsonify({"message": "You are not authorized to add this customer event"}), 403

#     db = get_db_connection()
#     cursor = db.cursor(dictionary=True)

#     # customer_id and event_id check when adding
#     cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (data['customer_id'],))
#     customer = cursor.fetchone()
#     if not customer:
#         db.close()
#         return jsonify({"message": "Invalid customer_id: Customer does not exist"}), 400

#     cursor.execute("SELECT * FROM events WHERE event_id = %s", (data['event_id'],))
#     event = cursor.fetchone()
#     if not event:
#         db.close()
#         return jsonify({"message": "Invalid event_id: Event does not exist"}), 400
    
#     # check if participation date matches the event date
#     if data['participation_date'] != str(event['date']):
#         db.close()
#         return jsonify({"message": "Participation date must match the event date"}), 400
#     # add the customerevent
#     cursor.execute(
#         "INSERT INTO customerevents (customer_id, event_id, participation_date) VALUES (%s, %s, %s)",
#         (data['customer_id'], data['event_id'], data['participation_date'])
#     )
#     db.commit()
#     db.close()
#     return jsonify({"message": "Customer event added successfully!"}), 201

# @customerevents_bp.route('/<int:customerevent_id>', methods=['PUT'])
# @jwt_required()
# def update_customerevent(customerevent_id):
#     claims = get_jwt()
#     data = request.json
#     db = get_db_connection()
#     cursor = db.cursor(dictionary=True)

#     cursor.execute("SELECT * FROM customerevents WHERE customerevent_id = %s", (customerevent_id,))
#     customerevent = cursor.fetchone()
#     # a non-admin user can only update their own customerevents
#     if claims['role'] != 'admin' and (customerevent['customer_id'] != claims['id']  or data['customer_id'] != claims['id']):
#         db.close()
#         return jsonify({"message": "You are not authorized to update this customer event"}), 403
    
#     # check if the customerevent exists
#     if not customerevent:
#         db.close()
#         return jsonify({"message": "Invalid customerevent_id: Customer event does not exist"}), 400

#      # check if the customer and event exist when updating
#     cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (data['customer_id'],))
#     customer = cursor.fetchone()
#     if not customer:
#         db.close()
#         return jsonify({"message": "Invalid customer_id: Customer does not exist"}), 400

#     cursor.execute("SELECT * FROM events WHERE event_id = %s", (data['event_id'],))
#     event = cursor.fetchone()
#     if not event:
#         db.close()
#         return jsonify({"message": "Invalid event_id: Event does not exist"}), 400
    
#     # check if participation date matches the event date
#     if data['participation_date'] != str(event['date']):
#         db.close()
#         return jsonify({"message": "Participation date must match the event date"}), 400


#     # update the customerevent
#     cursor.execute(
#         "UPDATE customerevents SET customer_id = %s, event_id = %s, participation_date = %s WHERE customerevent_id = %s",
#         (data['customer_id'], data['event_id'], data['participation_date'], customerevent_id)
#     )
#     db.commit()
#     db.close()
#     return jsonify({"message": "Customer event updated successfully!"})

# @customerevents_bp.route('/<int:customerevent_id>', methods=['DELETE'])
# @jwt_required()
# def delete_customerevent(customerevent_id):
#     claims = get_jwt()
#     db = get_db_connection()
#     cursor = db.cursor(dictionary=True)

#     # check if the customerevent exists before deleting
#     cursor.execute("SELECT * FROM customerevents WHERE customerevent_id = %s", (customerevent_id,))
#     customerevent = cursor.fetchone()
#     if not customerevent:
#         db.close()
#         return jsonify({"message": "Invalid customerevent_id: Customer event does not exist"}), 400

#     # non-admin users can only delete their own customerevents
#     if claims['role'] != 'admin' and customerevent['customer_id'] != claims['id']:
#         db.close()
#         return jsonify({"message": "You are not authorized to delete this customer event"}), 403

#     # delete the customerevent
#     cursor.execute("DELETE FROM customerevents WHERE customerevent_id = %s", (customerevent_id,))
#     db.commit()
#     db.close()
#     return jsonify({"message": "Customer event deleted successfully!"})
