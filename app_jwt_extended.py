from flask import Flask, jsonify, request
from database import db
from customer import Customer
from order import Order
from datetime import timedelta
from flask_jwt_extended import JWTManager, create_access_token, jwt_required

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:...'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JWT_SECRET_KEY'] = 'tajny_kluc'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=10)

db.init_app(app)

jwt = JWTManager(app)

# token (autentifikácia)
@app.route('/generate-token', methods=['POST'])
def generate_token():
    email = request.json.get('email')
    password = request.json.get('password')

    if email == 'user@gmail.com' and password == 'word':

        token = create_access_token(identity=email)

        return jsonify({
            'token': token
        })

    return jsonify({
        'message': 'Invalid email or password'
    }), 401


# 1 Načítaj všetkých zákazníkov
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

# 2 Načítaj všetky objednávky
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

# 3 Načítaj všetky objednávky konkrétneho zákazníka
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
@app.route('/customers/<int:customer_id>/orders', methods=['POST'])
@jwt_required()
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

# 5 Uprav objednávku
@app.route('/orders/<int:order_id>', methods=['PUT'])
@jwt_required()
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


# 6 Zmaž objednávku
@app.route('/orders/<int:order_id>', methods=['DELETE'])
@jwt_required()
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