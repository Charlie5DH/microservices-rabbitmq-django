from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import UniqueConstraint

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@db:3306/main'
CORS(app)

db = SQLAlchemy(app)

class Product(db.Model):
    # the product is created in the django app, this app will catch an event
    # from RabbitMQ and it will create a new product, but we don't want to autoincrement
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    title = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200), nullable=False)

class ProductUser(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)

    UniqueConstraint('user_id', 'product_id', name='user_product_unique')

@app.route('/')
def index():
    return "Hello"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')