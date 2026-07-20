from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Product(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    description = db.Column(db.String(500))

    price = db.Column(db.Float, nullable=False)

    image = db.Column(db.String(200))

    stock = db.Column(db.Integer, default=0)

class Cart(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)

    quantity = db.Column(db.Integer, default=1)

    user = db.relationship("User", backref="cart_items")

    product = db.relationship("Product", backref="cart_items")

class Address(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    full_name = db.Column(db.String(100), nullable=False)

    phone_number = db.Column(db.String(15), nullable=False)

    line1 = db.Column(db.String(200), nullable=False)

    line2 = db.Column(db.String(200), nullable=False)

    line3 = db.Column(db.String(200))

    city = db.Column(db.String(100), nullable=False)

    state = db.Column(db.String(100), nullable=False)

    pincode = db.Column(db.String(10), nullable=False)

    is_default = db.Column(db.Boolean, default=False)

    user = db.relationship("User", backref="addresses")

class Order(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    address_id = db.Column(
        db.Integer,
        db.ForeignKey("address.id"),
        nullable=False
    )

    total_amount = db.Column(
        db.Float,
        nullable=False
    )

    payment_status = db.Column(
        db.String(20),
        default="Pending"
    )

    order_status = db.Column(
        db.String(20),
        default="Placed"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    user = db.relationship("User", backref="orders")

    address = db.relationship("Address")

class OrderItem(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("order.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id"),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

    order = db.relationship(
        "Order",
        backref="items"
    )

    product = db.relationship("Product")