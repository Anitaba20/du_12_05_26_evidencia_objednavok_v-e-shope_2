# tabuľky som do postgresu poslala cez data grip

from flask import Flask, jsonify, request
from database import db
from customer import Customer
from order import Order
from datetime import datetime, timedelta
from functools import wraps
import jwt


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:...'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

SECRET_KEY = 'tajny_kluc'

db.init_app(app)

# token (autentifikácia)
@app.route('/generate-token', methods=['POST'])
def generate_token():
    email = request.json.get('email')
    password = request.json.get('password')

    if email == 'user@gmail.com' and password == 'word':

        exp = datetime.utcnow() + timedelta(minutes=10)

        token = jwt.encode({
            'email': email,
            'exp': exp
        }, SECRET_KEY, algorithm='HS256')

        return jsonify({
            'token': token
        })

    return jsonify({
        'message': 'Invalid email or password'
    }), 401


# JWT decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = request.headers.get('Authorization')

        if not token:
            return jsonify({
                'message': 'Token is missing'
            }), 401

        try:
            token = token.split()[1]

            jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

        except:
            return jsonify({
                'message': 'Token is invalid'
            }), 401

        return f(*args, **kwargs)

    return decorated


# 1 Načítaj všetkých zákazníkov (GET /customers)
@app.route('/customers', methods=['GET'])
def get_customers():

    customers = Customer.query.all()

    result = []

    for customer in customers:
        result.append({
            'id': customer.id,
            'name': customer.name,
            'email': customer.email
        })

    return jsonify(result)


# 2 Načítaj všetky objednávky (GET /orders)
@app.route('/orders', methods=['GET'])
def get_orders():

    orders = Order.query.all()

    result = []

    for order in orders:
        result.append({
            'id': order.id,
            'customer_id': order.customer_id,
            'product_name': order.product_name,
            'quantity': order.quantity,
            'order_date': str(order.order_date)
        })

    return jsonify(result)


# filtrovanie
# 3 Načítaj všetky objednávky konkrétneho zákazníka
# (GET /customers/<customer_id>/orders)
@app.route('/customers/<int:customer_id>/orders', methods=['GET'])
def get_customer_orders(customer_id):

    orders = Order.query.filter_by(customer_id=customer_id).all()

    result = []

    for order in orders:
        result.append({
            'id': order.id,
            'customer_id': order.customer_id,
            'product_name': order.product_name,
            'quantity': order.quantity,
            'order_date': str(order.order_date)
        })

    return jsonify(result)


# 4 Pridaj novú objednávku zákazníkovi
# (POST /customers/<customer_id>/orders)
@app.route('/customers/<int:customer_id>/orders', methods=['POST'])
@token_required
def add_order(customer_id):

    new_order = Order(
        customer_id=customer_id,
        product_name=request.json['product_name'],
        quantity=request.json['quantity']
    )

    db.session.add(new_order)
    db.session.commit()

    return jsonify({
        'message': 'Order added'
    }), 201


# 5 Uprav objednávku (PUT /orders/<order_id>)
@app.route('/orders/<int:order_id>', methods=['PUT'])
@token_required
def update_order(order_id):

    order = Order.query.get(order_id)

    if order:
        order.product_name = request.json['product_name']
        order.quantity = request.json['quantity']

        db.session.commit()

        return jsonify({
            'message': 'Order updated'
        })

    return jsonify({
        'error': 'Order not found'
    }), 404


# 6 Zmaž objednávku (DELETE /orders/<order_id>)
@app.route('/orders/<int:order_id>', methods=['DELETE'])
@token_required
def delete_order(order_id):

    order = Order.query.get(order_id)

    if order:
        db.session.delete(order)
        db.session.commit()

        return jsonify({
            'message': 'Order deleted'
        })

    return jsonify({
        'error': 'Order not found'
    }), 404


if __name__ == '__main__':
    app.run()