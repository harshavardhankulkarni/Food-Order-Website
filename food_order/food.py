import os

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required

from sqlalchemy.exc import IntegrityError, StatementError
from werkzeug.utils import secure_filename

from food_order import app, db, Category, admin_only, allowed_file, Food


# ################################ Manage Food section Start ##########################################################
@app.route("/food-order/manage-food")
@login_required
@admin_only
def manage_food():
    with app.app_context():
        all_food = db.session.query(Food).all()
        return render_template("admin/manage_food.html", foods=all_food)


# Add food
@app.route("/food-order/add-food", methods=["POST", "GET"])
@login_required
@admin_only
def add_food():
    with app.app_context():
        all_category = db.session.query(Category).all()
        if request.method == "POST":
            try:
                new_food = Food(
                    title=request.form.get("title"),
                    description=request.form.get("description"),
                    price=float(request.form.get("price")),
                    food=Category.query.filter_by(
                        id=request.form.get("category")
                    ).first(),
                    image_name=request.files.get("image").filename,
                    featured=request.form.get("featured"),
                    active=request.form.get("active"),
                )
                db.session.add(new_food)
                db.session.commit()
                file = request.files["image"]
                if not file.filename == "":
                    if file and allowed_file(file.filename):
                        if not os.path.isfile(f"food_order/static/images/{file.filename}"):
                            filename = secure_filename(file.filename)
                            file.save(
                                os.path.join(app.config["UPLOAD_FOLDER"], filename)
                            )
                return redirect(url_for("manage_food"))
            except StatementError:
                flash("Price Must be in decimal format")
                return redirect(url_for("add_food"))
            except ValueError:
                flash("Price Must be in decimal format")
                return redirect(url_for("add_food"))
            except IntegrityError:
                flash("Make sure you select all fields")
                return redirect(url_for("add_food"))
        return render_template("admin/add_food.html", categories=all_category)


# Update food
@app.route("/food-order/update-food", methods=["POST", "GET"])
@login_required
@admin_only
def update_food():
    with app.app_context():
        all_category = db.session.query(Category).all()
        food = Food.query.get(request.args.get("id"))
        if request.method == "POST":
            try:
                food.title = request.form.get("title")
                food.description = request.form.get("description")
                food.price = float(request.form.get("price"))
                food.food = Category.query.filter_by(
                    id=request.form.get("category")
                ).first()
                if not request.files.get("image").filename == "":
                    food.image_name = request.files.get("image").filename
                food.featured = request.form.get("featured")
                food.active = request.form.get("active")
                db.session.commit()
                return redirect(url_for("manage_food"))
            except StatementError:
                flash("Price Must be in decimal format")
                return redirect(url_for("add_food"))
            except ValueError:
                flash("Price Must be in decimal format")
                return redirect(url_for("add_food"))
            except IntegrityError:
                flash("Make sure you select all fields")
                return redirect(url_for("add_food"))
        return render_template(
            "admin/update_food.html", food=food, categories=all_category
        )


# Delete a food
@app.route("/food-order/delete-food", methods=["POST", "GET"])
@login_required
@admin_only
def delete_food():
    with app.app_context():
        food = Food.query.get(request.args.get("id"))
        db.session.delete(food)
        db.session.commit()
        return redirect(url_for("manage_food"))

# ################################## Manage Food section End ##########################################################
