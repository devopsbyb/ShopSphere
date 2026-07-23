from flask import render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User


def register_auth_routes(app):

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

            return "User Registered Successfully!"

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