from flask import render_template, request, redirect, session   
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Product, Cart 


def register_routes(app):
    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]
            confirm_password = request.form["confirm_password"]

            if password != confirm_password:
                return "Passwords do not match"

            hashed_password = generate_password_hash(password)

            new_user = User(
                username=username,
                email=email,
                password=hashed_password,
            )

            db.session.add(new_user)
            db.session.commit()

            return "User Registered Successfully!"

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]

            user = User.query.filter_by(email=email).first()

            if user and check_password_hash(user.password, password):
                session["user_id"] = user.id
                session["username"] = user.username
                return redirect("/products")

            return "Invalid email or password"

        return render_template("login.html")

    @app.route("/products")
    def products():
        if "user_id" not in session:
            return redirect("/login")

        products = Product.query.all()

        return render_template("products.html", products=products)

    @app.route("/add-to-cart/<int:product_id>", methods=["POST"])
    def add_to_cart(product_id):
        if "user_id" not in session:
            return redirect("/login")

        cart_item = Cart.query.filter_by(
            user_id=session["user_id"],
            product_id=product_id,
        ).first()

        if cart_item:
            cart_item.quantity += 1
        else:
            cart_item = Cart(
                user_id=session["user_id"],
                product_id=product_id,
                quantity=1,
            )
            db.session.add(cart_item)

        db.session.commit()

        return redirect("/cart")

    @app.route("/cart")
    def cart():
        if "user_id" not in session:
            return redirect("/login")

        cart_items = Cart.query.filter_by(user_id=session["user_id"]).all()

        total = sum(item.product.price * item.quantity for item in cart_items)

        return render_template(
            "cart.html",
            cart_items=cart_items,
            total=total,
        )
    
    @app.route("/remove-from-cart/<int:cart_id>", methods=["POST"])
    def remove_from_cart(cart_id):
        if "user_id" not in session:
            return redirect("/login")

        cart_item = Cart.query.get_or_404(cart_id)

        if cart_item.user_id != session["user_id"]:
            return redirect("/cart")

        if cart_item.quantity > 1:
           cart_item.quantity -= 1
        else:
          db.session.delete(cart_item)

        db.session.commit()  
        return redirect("/cart")

    @app.route("/checkout")
    def checkout():
        return render_template("checkout.html")

    @app.route("/order-success")
    def order_success():
        return render_template("order_success.html")