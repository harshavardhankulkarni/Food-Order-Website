from datetime import datetime

from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from food_order import (
    app,
    db,
    Food,
    Category,
    Admin,
    Order,
    login_required_for_customer,
)


def current_date():
    return datetime.now().strftime("%Y-%m-%d")


@app.route("/")
def index():
    with app.app_context():
        all_category = db.session.query(Category).all()
        all_food = db.session.query(Food).all()
        return render_template(
            "index.html", foods=all_food[:4], categories=all_category
        )


@app.route("/order", methods=["GET", "POST"])
@login_required_for_customer
def order():
    with app.app_context():
        food = Food.query.get(request.args.get("id"))
        if request.method == "POST":
            try:
                new_order = Order(
                    order_date=current_date(),
                    qty=abs(int(request.form.get("qty"))),
                    customer_name=current_user.full_name,
                    customer_contact=request.form.get("contact"),
                    customer_email=request.form.get("email"),
                    customer_address=request.form.get("address"),
                    total=(food.price * float(request.form.get("qty"))),
                    order=food,
                    customer=current_user,
                    status="Ordered",
                )
                db.session.add(new_order)
                db.session.commit()
            except IntegrityError:
                flash("You have to fill all fields")
        return render_template("order.html", food=food)


@app.route("/order-status")
@login_required_for_customer
def order_status():
    with app.app_context():
        orders = [
            o for o in db.session.query(Order).all() if o.customer_id == current_user.id
        ]
        return render_template("order_status.html", orders=orders)


@app.route("/order-cancelled")
@login_required_for_customer
def order_cancelled():
    with app.app_context():
        order_detail = Order.query.get(request.args.get("id"))
        order_detail.status = "Cancelled"
        db.session.commit()
        return redirect(url_for("order_status"))


@app.route("/foods")
def foods():
    with app.app_context():
        all_food = db.session.query(Food).all()
        return render_template("foods.html", foods=all_food)


@app.route("/categories")
def categories():
    with app.app_context():
        all_category = db.session.query(Category).all()
        return render_template("categories.html", categories=all_category)


@app.route("/category-food")
def category_food():
    with app.app_context():
        category = Category.query.get(request.args.get("id"))
        food = db.session.query(Food).all()
        all_food = [f for f in food if f.category_id == category.id]
        return render_template("category-foods.html", category=category, foods=all_food)


@app.route("/food-search", methods=["POST"])
def food_search():
    if request.method == "POST":
        with app.app_context():
            food = db.session.query(Food).all()
            all_food = [
                f for f in food if request.form.get("search").lower() in f.title.lower()
            ]
            return render_template(
                "food-search.html", foods=all_food, search=request.form.get("search")
            )


@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if not current_user.is_authenticated:
        if request.method == "POST":
            try:
                with app.app_context():
                    if request.form.get("password") == request.form.get("c-password"):
                        new_customer = Admin(
                            full_name=request.form.get("full_name"),
                            username=request.form.get("username"),
                            password=generate_password_hash(
                                request.form.get("password"), salt_length=8
                            ),
                            role="customer",
                        )
                        db.session.add(new_customer)
                        db.session.commit()
                        flash("Signup Successful", "success")
                        return redirect(url_for("login"))
                    else:
                        flash("Password Doesn't match", "warning")
                        return redirect(url_for("sign_up"))
            except IntegrityError:
                flash("Username already exists", "warning")
                return redirect(url_for("sign_up"))
        return render_template("sign_up.html")
    return redirect(url_for("index"))
