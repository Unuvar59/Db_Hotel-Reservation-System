from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restx import Api

from routes_swagger.customers import customers_bp, api as customers_api
from routes_swagger.reservations import reservations_bp, api as reservations_api
from routes_swagger.payments import payments_bp, api as payments_api
from routes_swagger.customerevents import customerevents_bp, api as customerevents_api
from routes_swagger.employees import employees_bp, api as employees_api
from routes_swagger.events import events_bp, api as events_api
from routes_swagger.feedback import feedback_bp, api as feedback_api
from routes_swagger.rooms import rooms_bp, api as rooms_api
from routes_swagger.roomservices import roomservices_bp, api as roomservices_api

from routes_swagger.auth import auth_ns

# add JWT token to Swagger UI for authorization
authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Add a JWT with **Bearer <JWT token>**"
    }
}

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'very-secure-key'
jwt = JWTManager(app)

# Swagger API instance
api = Api(app, version='1.0', title='Hotel Reservation API',
          description='API documentation for the Hotel Reservation System.',
          authorizations=authorizations,  # authorization configuration
          security='Bearer')  # default security for all endpoints

# Blueprint
app.register_blueprint(customers_bp, url_prefix='/api/customers')
app.register_blueprint(reservations_bp, url_prefix='/api/reservations')
app.register_blueprint(payments_bp, url_prefix='/api/payments')
app.register_blueprint(customerevents_bp, url_prefix='/api/customerevents')
app.register_blueprint(employees_bp, url_prefix='/api/employees')
app.register_blueprint(events_bp, url_prefix='/api/events')
app.register_blueprint(feedback_bp, url_prefix='/api/feedback')
app.register_blueprint(rooms_bp, url_prefix='/api/rooms')
app.register_blueprint(roomservices_bp, url_prefix='/api/roomservices')

# Swagger API namespaces
api.add_namespace(auth_ns, path='/api/auth')  
api.add_namespace(customers_api, path='/api/customers')
api.add_namespace(reservations_api, path='/api/reservations')
api.add_namespace(payments_api, path='/api/payments')
api.add_namespace(customerevents_api, path='/api/customerevents')
api.add_namespace(employees_api, path='/api/employees')
api.add_namespace(events_api, path='/api/events')
api.add_namespace(feedback_api, path='/api/feedback')
api.add_namespace(rooms_api, path='/api/rooms')
api.add_namespace(roomservices_api, path='/api/roomservices')

if __name__ == '__main__':
    app.run(debug=True)
    