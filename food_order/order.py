from flask import render_template, request, redirect, url_for
from flask_login import login_required

from food_order import app, db, admin_only, Order


# ################################## Manage Order section Start #######################################################
@app.route("/food-order/manage-order")
@login_required
@admin_only
def manage_order():
    with app.app_context():
        orders = db.session.query(Order).all()
        return render_template("admin/manage_order.html", orders=orders)


# Update order
@app.route("/food-order/update-order", methods=["POST", "GET"])
@login_required
@admin_only
def update_order():
    with app.app_context():
        order_detail = Order.query.get(request.args.get("id"))
        if request.method == "POST":
            order_detail.qty = request.form.get("qty")
            order_detail.customer_name = request.form.get("customer_name")
            order_detail.status = request.form.get("status")
            order_detail.customer_contact = request.form.get("customer_contact")
            order_detail.customer_address = request.form.get("customer_address")
            order_detail.customer_email = request.form.get("customer_email")
            db.session.commit()
            return redirect(url_for("manage_order"))
        return render_template("admin/update_order.html", order=order_detail)

# ################################## Manage Order section End #########################################################
