from app import app
from models import db, Product

with app.app_context():

    # Clear existing products (optional during development)
    Product.query.delete()

    products = [
        Product(
            name="Wireless Mouse",
            description="Ergonomic wireless mouse",
            price=799.0,
            image="mouse.jpg",
            stock=25
        ),
        Product(
            name="Mechanical Keyboard",
            description="RGB Mechanical Keyboard",
            price=2999.0,
            image="keyboard.jpg",
            stock=15
        ),
        Product(
            name="Gaming Headset",
            description="7.1 Surround Gaming Headset",
            price=1999.0,
            image="headset.jpg",
            stock=20
        ),
        Product(
            name="USB-C Hub",
            description="6-in-1 USB-C Hub",
            price=1499.0,
            image="hub.jpg",
            stock=30
        )
    ]

    db.session.add_all(products)
    db.session.commit()

    print("Products inserted successfully!")