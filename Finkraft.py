from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_httpauth import HTTPBasicAuth
from flask_pymongo import PyMongo
import sqlite3

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()

# Simple SQLite database for user data
users = {
    'username': 'password',
}

# SQLite database initialization
conn = sqlite3.connect('user_database.db', check_same_thread=False)
cursor = conn.cursor()

# Create users table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
''')
conn.commit()

# Flask route to add a new user
@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    # Check if the username already exists
    existing_user = cursor.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 400

    # Insert the new user into the database
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()

    return jsonify({'message': 'User added successfully'})

# Flask route to delete a user
@app.route('/delete_user/<username>', methods=['DELETE'])
def delete_user(username):
    # Check if the user exists
    existing_user = cursor.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
    if not existing_user:
        return jsonify({'error': 'User not found'}), 404

    # Delete the user from the database
    cursor.execute('DELETE FROM users WHERE username=?', (username,))
    conn.commit()

    return jsonify({'message': 'User deleted successfully'})

# Flask route to get information about a user
@app.route('/get_user/<username>', methods=['GET'])
def get_user(username):
    # Retrieve the user from the database
    user = cursor.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    user_info = {'id': user[0], 'username': user[1], 'password': user[2]}
    return jsonify({'user': user_info})

# Simple MongoDB database for product catalog data
products = [
    {'id': 1, 'name': 'Product 1', 'price': 19.99},
    {'id': 2, 'name': 'Product 2', 'price': 29.99},
]

# Configure MongoDB connection
app.config['MONGO_URI'] = 'mongodb://localhost:27017/product_database'
mongo = PyMongo(app)

# Flask route to add a new product
@app.route('/add_product', methods=['POST'])
def add_product():
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')

    if not name or not price:
        return jsonify({'error': 'Name and price are required'}), 400

    # Insert the new product into the database
    product_id = mongo.db.products.insert_one({'name': name, 'price': price}).inserted_id

    return jsonify({'message': 'Product added successfully', 'product_id': str(product_id)})

# Flask route to delete a product
@app.route('/delete_product/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    # Check if the product exists
    existing_product = mongo.db.products.find_one({'_id': product_id})
    if not existing_product:
        return jsonify({'error': 'Product not found'}), 404

    # Delete the product from the database
    mongo.db.products.delete_one({'_id': product_id})

    return jsonify({'message': 'Product deleted successfully'})

# Flask route to get information about a product
@app.route('/get_product/<product_id>', methods=['GET'])
def get_product(product_id):
    # Retrieve the product from the database
    product = mongo.db.products.find_one({'_id': product_id})

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    return jsonify({'product': product})

# Authentication callback
@auth.verify_password
def verify_password(username, password):
    return users.get(username) == password

# Resource to get a list of products
class ProductListResource(Resource):
    @auth.login_required
    def get(self):
        return {'products': products}

# Resource to get details of a specific product
class ProductResource(Resource):
    @auth.login_required
    def get(self, product_id):
        product = next((p for p in products if p['id'] == product_id), None)
        if product:
            return product
        else:
            return {'error': 'Product not found'}, 404

# Add resources to the API
api.add_resource(ProductListResource, '/products')
api.add_resource(ProductResource, '/products/<int:product_id>')

if __name__ == '__main__':
    app.run(debug=True)