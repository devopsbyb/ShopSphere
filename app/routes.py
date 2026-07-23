from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config
from models import Address, Cart, Product, User, Order, OrderItem, db
from templates.razorpay_client import client


def register_routes(app):
    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if "user_id" in session:
            return redirect("/products")

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

            return redirect("/login")

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if "user_id" in session:
            return redirect("/products")

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

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect("/login")

    @app.route("/products")
    def products():
        if "user_id" not in session:
            return redirect("/login")

        products = Product.query.all()

        cart_items = Cart.query.filter_by(
            user_id=session["user_id"]
        ).all()

        cart_dict = {
            item.product_id: item.quantity
            for item in cart_items
        }

        return render_template(
            "products.html",
            products=products,
            cart_dict=cart_dict,
        )

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

        return redirect("/products")

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

    @app.route("/increase-quantity/<int:cart_id>", methods=["POST"])
    def increase_quantity(cart_id):
        if "user_id" not in session:
            return redirect("/login")

        cart_item = Cart.query.get_or_404(cart_id)

        if cart_item.user_id != session["user_id"]:
            return redirect("/cart")

        cart_item.quantity += 1
        db.session.commit()

        return redirect("/cart")
    
    @app.route("/decrease-quantity/<int:cart_id>", methods=["POST"])
    def decrease_quantity(cart_id):
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
    
    @app.route("/decrease-cart/<int:product_id>", methods=["POST"])
    def decrease_cart(product_id):
        if "user_id" not in session:
            return redirect("/login")

        cart_item = Cart.query.filter_by(
            user_id=session["user_id"],
            product_id=product_id
        ).first()

        if cart_item:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                db.session.delete(cart_item)

            db.session.commit()

        return redirect("/products")

    @app.route("/checkout")
    def checkout():
        if "user_id" not in session:
            return redirect("/login")

        cart_items = Cart.query.filter_by(user_id=session["user_id"]).all()

        total = sum(item.product.price * item.quantity for item in cart_items)

        return render_template(
            "checkout.html",
            cart_items=cart_items,
            total=total,
        )

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

    @app.route("/delete-address/<int:address_id>", methods=["POST"])
    def delete_address(address_id):
        if "user_id" not in session:
            return redirect("/login")

        address = Address.query.get_or_404(address_id)

        if address.user_id != session["user_id"]:
            return redirect("/addresses")

        db.session.delete(address)
        db.session.commit()

        return redirect("/addresses")

    @app.route("/edit-address/<int:address_id>", methods=["GET", "POST"])
    def edit_address(address_id):
        if "user_id" not in session:
            return redirect("/login")

        address = Address.query.get_or_404(address_id)

        if address.user_id != session["user_id"]:
            return redirect("/addresses")

        if request.method == "POST":
            address.full_name = request.form["full_name"]
            address.phone_number = request.form["phone_number"]
            address.line1 = request.form["line1"]
            address.line2 = request.form["line2"]
            address.line3 = request.form["line3"]
            address.city = request.form["city"]
            address.state = request.form["state"]
            address.pincode = request.form["pincode"]

            if "is_default" in request.form:
                Address.query.filter_by(user_id=session["user_id"]).update({"is_default": False})
                address.is_default = True
            else:
                address.is_default = False

            db.session.commit()
            return redirect("/addresses")

        return render_template("edit_address.html", address=address)

    @app.route("/select-address/<int:address_id>", methods=["POST"])
    def select_address(address_id):
        if "user_id" not in session:
            return redirect("/login")

        address = Address.query.get_or_404(address_id)

        if address.user_id != session["user_id"]:
            return redirect("/addresses")

        session["selected_address_id"] = address.id

        return redirect("/order-review")

    @app.route("/order-review")
    def order_review():
        if "user_id" not in session:
            return redirect("/login")

        if "selected_address_id" not in session:
            return redirect("/addresses")

        address = Address.query.get_or_404(session["selected_address_id"])
        cart_items = Cart.query.filter_by(user_id=session["user_id"]).all()

        total = 0
        for item in cart_items:
            total += item.product.price * item.quantity

        return render_template(
            "order_review.html",
            address=address,
            cart_items=cart_items,
            total=total,
        )

    @app.route("/place-order", methods=["POST"])
    def place_order():
        if "user_id" not in session:
            return redirect("/login")

        if "selected_address_id" not in session:
            return redirect("/addresses")

        cart_items = Cart.query.filter_by(user_id=session["user_id"]).all()

        if not cart_items:
            return redirect("/cart")

        total = 0
        for item in cart_items:
            total += item.product.price * item.quantity

        order = Order(
            user_id=session["user_id"],
            address_id=session["selected_address_id"],
            total_amount=total,
        )

        db.session.add(order)
        db.session.commit()

        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.price,
            )
            db.session.add(order_item)

        db.session.commit()

        return redirect(f"/payment/{order.id}")

    @app.route("/payment/<int:order_id>")
    def payment(order_id):
        if "user_id" not in session:
            return redirect("/login")

        order = Order.query.get_or_404(order_id)

        if order.user_id != session["user_id"]:
            return redirect("/products")

        razorpay_order = client.order.create({
            "amount": int(order.total_amount * 100),  # paise
            "currency": "INR",
            "receipt": f"order_{order.id}"
        })

        return render_template(
            "payment.html",
            order=order,
            razorpay_order_id=razorpay_order["id"],
            razorpay_key=Config.RAZORPAY_KEY_ID
        )

    @app.route("/payment-success/<int:order_id>", methods=["POST"])
    def payment_success(order_id):
        if "user_id" not in session:
            return redirect("/login")

        order = Order.query.get_or_404(order_id)

        if order.user_id != session["user_id"]:
            return redirect("/products")
        order.payment_status = "Paid"

        db.session.commit()

        Cart.query.filter_by(
            user_id=session["user_id"]
        ).delete()

        db.session.commit()

        return render_template(
            "order_success.html",
            order=order,
        )

    @app.route("/my-orders")
    def my_orders():
        if "user_id" not in session:
            return redirect("/login")

        orders = Order.query.filter_by(user_id=session["user_id"]).order_by(Order.created_at.desc()).all()

        return render_template("my_orders.html", orders=orders)

    @app.route("/test-razorpay")
    def test_razorpay():
        try:
            order = client.order.create({
                "amount": 100,
                "currency": "INR",
                "receipt": "test_receipt"
            })

            return order

        except Exception as e:
            return str(e)
        
    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():

        if request.method == "POST":

            email = request.form["email"]
            password = request.form["password"]

            user = User.query.filter_by(email=email).first()

            if (
                user
                and check_password_hash(user.password, password)
                and user.is_admin
            ):

                session["admin_id"] = user.id
                session["admin_name"] = user.username

                return redirect("/admin/dashboard")

            return "Invalid Admin Credentials"

        return render_template("admin/login.html")    
    
    @app.route("/admin/dashboard")
    def admin_dashboard():

        if "admin_id" not in session:
            return redirect("/admin/login")

        return render_template("admin/dashboard.html")