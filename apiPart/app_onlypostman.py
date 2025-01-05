from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restx import Api

from routes.customers import customers_bp
from routes.reservations import reservations_bp
from routes.payments import payments_bp
from routes.customerevents import customerevents_bp
from routes.employees import employees_bp
from routes.events import events_bp
from routes.feedback import feedback_bp
from routes.rooms import rooms_bp
from routes.roomservices import roomservices_bp

from routes_swagger.auth import auth_bp

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'very-secure-key'
jwt = JWTManager(app)

# Swagger API instance
api = Api(app, version='1.0', title='Hotel Reservation API',
          description='API documentation for the Hotel Reservation System.')

# Blueprint
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(customers_bp, url_prefix='/api/customers')
app.register_blueprint(reservations_bp, url_prefix='/api/reservations')
app.register_blueprint(payments_bp, url_prefix='/api/payments')
app.register_blueprint(customerevents_bp, url_prefix='/api/customerevents')
app.register_blueprint(employees_bp, url_prefix='/api/employees')
app.register_blueprint(events_bp, url_prefix='/api/events')
app.register_blueprint(feedback_bp, url_prefix='/api/feedback')
app.register_blueprint(rooms_bp, url_prefix='/api/rooms')
app.register_blueprint(roomservices_bp, url_prefix='/api/roomservices')

if __name__ == '__main__':
    app.run(debug=True)
    