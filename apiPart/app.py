from flask import Flask
from flask_jwt_extended import JWTManager
from routes.customers import customers_bp
from routes.reservations import reservations_bp
from routes.payments import payments_bp
from utils.auth import auth_bp

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'very-secure-key'
jwt = JWTManager(app)

# Blueprint
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(customers_bp, url_prefix='/api/customers')
app.register_blueprint(reservations_bp, url_prefix='/api/reservations')
app.register_blueprint(payments_bp, url_prefix='/api/payments')

if __name__ == '__main__':
    app.run(debug=True)
    