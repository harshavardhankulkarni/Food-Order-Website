from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from food_order import app, db, Food, Category, Admin, Order, admin_only, super_admin


# ##################################### Admin Section #################################################################
@app.route("/food-order/admin", methods=["GET", "POST"])
def admin_index():
    with app.app_context():
        all_category = db.session.query(Category).all()
        all_food = db.session.query(Food).all()
        all_order = db.session.query(Order).all()
        total = [o.total for o in all_order if o.status == "Delivered"]
        if request.method == "POST":
            admin = Admin.query.filter_by(username=request.form.get("username")).first()
            if admin:
                if check_password_hash(admin.password, request.form.get("password")):
                    if admin.role == "admin":
                        login_user(admin)
                        return redirect(url_for("admin_index"))
                    else:
                        flash("Something went wrong")
                        return redirect(url_for("admin_index"))
                else:
                    flash("Password incorrect, please try again")
                    return redirect(url_for("admin_index"))
            else:
                flash("username not found")
                return redirect(url_for("admin_index"))
        return render_template(
            "admin/index.html",
            category_count=len(all_category),
            food_count=len(all_food),
            order_count=len(all_order),
            total_revenue=sum(total),
        )


# ############################## Manage admin section Start ###########################################################
@app.route("/food-order/manage-admin")
@login_required
@admin_only
@super_admin
def manage_admin():
    with app.app_context():
        admins = [
            admin
            for admin in Admin.query.order_by(Admin.id).all()
            if admin.role == "admin"
        ]
        return render_template("admin/manage_admin.html", admins=admins)


# Add the admin
@app.route("/food-order/add-admin", methods=["POST", "GET"])
@login_required
@admin_only
@super_admin
def add_admin():
    if request.method == "POST":
        try:
            with app.app_context():
                new_admin = Admin(
                    full_name=request.form.get("full_name"),
                    username=request.form.get("username"),
                    password=generate_password_hash(request.form.get("password"), salt_length=8),
                    role="admin",
                )
                db.session.add(new_admin)
                db.session.commit()
                return redirect(url_for("manage_admin"))
        except IntegrityError:
            flash("Username already exists")
            return redirect(url_for("add_admin"))
    return render_template("admin/add_admin.html")


# Update Admin information
@app.route("/food-order/update-admin/", methods=["POST", "GET"])
@login_required
@admin_only
@super_admin
def update_admin():
    with app.app_context():
        try:
            admin = Admin.query.get(request.args.get("id"))
            if request.method == "POST":
                admin.full_name = request.form.get("full_name")
                admin.username = request.form.get("username")
                db.session.commit()
                return redirect(url_for("manage_admin"))
        except IntegrityError:
            flash("Username already exists")
            return redirect(url_for("update_admin"))
        return render_template("admin/update_admin.html", admin=admin)


# Change password for admin
@app.route("/food-order/change-admin-password/", methods=["POST", "GET"])
@login_required
@admin_only
@super_admin
def change_password():
    with app.app_context():
        admin = Admin.query.get(request.args.get("id"))
        if request.method == "POST":
            if check_password_hash(
                    admin.password, request.form.get("current_password")
            ):
                if request.form.get("new_password") == request.form.get(
                        "confirm_password"
                ):
                    admin.password = generate_password_hash(
                        request.form.get("confirm_password"), salt_length=8
                    )
                    db.session.commit()
                    return redirect(url_for("manage_admin", admin=admin))
                else:
                    flash("Password does not match")
                    return redirect(url_for("change_password", id=admin.id))
            else:
                flash("This is not a valid admin password")
                return redirect(url_for("change_password", id=admin.id))
        return render_template("admin/change_password.html", admin=admin)


# Delete admin
@app.route("/food-order/delete-admin/")
@login_required
@admin_only
def delete_admin():
    with app.app_context():
        admin = Admin.query.get(request.args.get("id"))
        db.session.delete(admin)
        db.session.commit()
        return redirect(url_for("manage_admin"))


# Logout
@app.route("/food-order/admin/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("admin_index"))

# ############################## Manage admin section End #############################################################
