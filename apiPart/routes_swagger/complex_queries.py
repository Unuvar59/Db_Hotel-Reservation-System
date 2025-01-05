from flask import Blueprint, jsonify
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from models.database import get_db_connection

# Blueprint and Namespace for Complex Queries
complex_queries_bp = Blueprint('complex_queries', __name__)
api = Namespace('Complex Queries', description='Endpoints for complex SQL queries')

# Swagger Models
customer_reservations_model = api.model('CustomerReservations', {
    'Customer_Name': fields.String,
    'Total_Reservations': fields.Integer
})

employees_positions_model = api.model('EmployeesPositions', {
    'position': fields.String,
    'Total_Employees': fields.Integer
})

recent_reservations_model = api.model('RecentReservations', {
    'Customer_Name': fields.String,
    'Room_Type': fields.String,
    'check_in_date': fields.String,
    'check_out_date': fields.String
})

# Query 1: Customer Reservations Count
@api.route('/customers-reservations')
class CustomersReservations(Resource):
    @api.doc(description="Lists how many reservations each customer has made.")
    @api.response(200, 'Success', [customer_reservations_model])
    @jwt_required()
    def get(self):
        """Lists how many reservations each customer has made"""
        claims = get_jwt()
        current_user_email = get_jwt_identity()

        # Query based on role
        if claims['role'] == 'admin':
            query = """
            SELECT 
                C.name AS Customer_Name,
                COUNT(Res.reservation_id) AS Total_Reservations
            FROM 
                Customers C
            LEFT JOIN 
                Reservations Res ON C.customer_id = Res.customer_id
            GROUP BY 
                C.name
            ORDER BY 
                Total_Reservations DESC;
            """
            params = None
        elif claims['role'] == 'user':
            query = """
            SELECT 
                C.name AS Customer_Name,
                COUNT(Res.reservation_id) AS Total_Reservations
            FROM 
                Customers C
            LEFT JOIN 
                Reservations Res ON C.customer_id = Res.customer_id
            WHERE 
                C.e_mail = %s
            GROUP BY 
                C.name
            ORDER BY 
                Total_Reservations DESC;
            """
            params = (current_user_email,)
        else:
            return {"message": "Access denied"}, 403

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
        except Exception as e:
            db.close()
            return {"message": "Error retrieving data", "error": str(e)}, 500

        db.close()
        return jsonify(results)

# Query 2: Employees Positions Count
@api.route('/employees-positions')
class EmployeesPositions(Resource):
    @api.doc(description="Lists the number of employees based on their positions.")
    @api.response(200, 'Success', [employees_positions_model])
    @jwt_required()
    def get(self):
        """Lists the number of employees based on their positions"""
        claims = get_jwt()

        # Only allow access to admins
        if claims['role'] != 'admin':
            return {"message": "Access denied"}, 403

        query = """
        SELECT 
            E.position,
            COUNT(E.employee_id) AS Total_Employees
        FROM 
            Employees E
        GROUP BY 
            E.position
        ORDER BY 
            Total_Employees DESC;
        """
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(query)
            results = cursor.fetchall()
        except Exception as e:
            db.close()
            return {"message": "Error retrieving data", "error": str(e)}, 500

        db.close()
        return jsonify(results)

# Query 3: Recent Reservations
@api.route('/recent-reservations')
class RecentReservations(Resource):
    @api.doc(description="Lists all reservations made in the last 3 months.")
    @api.response(200, 'Success', [recent_reservations_model])
    @jwt_required()
    def get(self):
        """Lists all reservations made in the last 3 months"""
        claims = get_jwt()

        # Only allow access to admins
        if claims['role'] != 'admin':
            return {"message": "Access denied"}, 403

        query = """
        SELECT 
            C.name AS Customer_Name,
            R.type AS Room_Type,
            Res.check_in_date,
            Res.check_out_date
        FROM 
            Reservations Res
        JOIN 
            Customers C ON Res.customer_id = C.customer_id
        JOIN 
            Rooms R ON Res.room_id = R.room_id
        WHERE 
            Res.check_in_date >= DATE_ADD(CURDATE(), INTERVAL -3 MONTH)
        ORDER BY 
            Res.check_in_date DESC;
        """
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(query)
            results = cursor.fetchall()
        except Exception as e:
            db.close()
            return {"message": "Error retrieving data", "error": str(e)}, 500

        db.close()
        return jsonify(results)
