from flask import render_template, request, redirect, session   
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Product, Cart,Address 


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

        valid_cart_items = [item for item in cart_items if item.product]

        total = sum(item.product.price * item.quantity for item in valid_cart_items)

        return render_template(
            "cart.html",
            cart_items=valid_cart_items,
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

    @app.route("/add-address", methods=["GET", "POST"])
    def add_address():
        if "user_id" not in session:
            return redirect("/login")

        if request.method == "POST":
            full_name = request.form["full_name"]
            phone_number = request.form["phone_number"]
            line1 = request.form["line1"]
            line2 = request.form["line2"]
            line3 = request.form["line3"]
            city = request.form["city"]
            state = request.form["state"]
            pincode = request.form["pincode"]

            is_default = "is_default" in request.form

            if is_default:
                Address.query.filter_by(user_id=session["user_id"]).update({"is_default": False})

            new_address = Address(
                user_id=session["user_id"],
                full_name=full_name,
                phone_number=phone_number,
                line1=line1,
                line2=line2,
                line3=line3,
                city=city,
                state=state,
                pincode=pincode,
                is_default=is_default,
            )

            db.session.add(new_address)
            db.session.commit()

            return redirect("/addresses")

        return render_template("add_address.html")
    
    @app.route("/addresses")
    def addresses():
        if "user_id" not in session:
            return redirect("/login")

        addresses = Address.query.filter_by(user_id=session["user_id"]).all()

        return render_template("addresses.html", addresses=addresses)