from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from food_order import app, db, User, login_required_for_customer, admin_only


# ############################## Manage Customers section Start #######################################################
@app.route("/food-order/manage-customer")
@login_required
@admin_only
def manage_customer():
    with app.app_context():
        customers = [
            customer
            for customer in User.query.order_by(User.id).all()
            if customer.role == "customer"
        ]
        return render_template("admin/manage_customer.html", customers=customers)


# Add the Customer
@app.route("/food-order/add-customer", methods=["POST", "GET"])
@login_required
@admin_only
def add_customer():
    if request.method == "POST":
        try:
            with app.app_context():
                new_customer = User(
                    full_name=request.form.get("full_name"),
                    username=request.form.get("username"),
                    password=generate_password_hash(request.form.get("password"), salt_length=8),
                    role="customer",
                )
                db.session.add(new_customer)
                db.session.commit()
                return redirect(url_for("manage_customer"))
        except IntegrityError:
            flash("Username already exists")
            return redirect(url_for("add_customer"))
    return render_template("admin/add_customer.html")


# Delete customer
@app.route("/food-order/delete-customer/")
@login_required
@admin_only
def delete_customer():
    with app.app_context():
        customer = User.query.get(request.args.get("id"))
        db.session.delete(customer)
        db.session.commit()
        return redirect(url_for("manage_customer"))


@app.route("/login", methods=["POST", "GET"])
def login():
    if not current_user.is_authenticated:
        if request.method == "POST":
            customer = User.query.filter_by(
                username=request.form.get("username")
            ).first()
            if customer:
                if check_password_hash(customer.password, request.form.get("password")):
                    login_user(customer)
                    flash("Login successful", "success")
                    return redirect(request.referrer)
                else:
                    flash("Password incorrect, please try again")
                    return redirect(url_for("login"))
            else:
                flash("username not found")
                return redirect(url_for("login"))
        return render_template("login.html")
    return redirect(url_for("index"))


# Logout customer
@app.route("/logout")
@login_required_for_customer
def logout_customer():
    logout_user()
    return redirect(request.referrer)

# ############################## Manage Customers section End #########################################################
