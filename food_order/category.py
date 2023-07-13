import os

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

from food_order import app, db, Category, admin_only, allowed_file


# ############################## Manage Category section Start ########################################################
@app.route("/food-order/manage-category")
@login_required
@admin_only
def manage_category():
    with app.app_context():
        all_category = db.session.query(Category).all()
        return render_template("admin/manage_category.html", categories=all_category)


# Add a new category
@app.route("/food-order/add-category", methods=["POST", "GET"])
@login_required
@admin_only
def add_category():
    if request.method == "POST":
        with app.app_context():
            try:
                new_category = Category(
                    title=request.form.get("title"),
                    image_name=request.files.get("image").filename,
                    featured=request.form.get("featured"),
                    active=request.form.get("active"),
                )
                db.session.add(new_category)
                db.session.commit()
                file = request.files["image"]
                if not file.filename == "":
                    if file and allowed_file(file.filename):
                        if not os.path.isfile(f"static/images/{file.filename}"):
                            filename = secure_filename(file.filename)
                            file.save(
                                os.path.join(app.config["UPLOAD_FOLDER"], filename)
                            )
                return redirect(url_for("manage_category"))
            except IntegrityError:
                flash("You have to select featured and active status.")
                return redirect(url_for("add_category"))
    return render_template("admin/add_category.html")


# Update category
@app.route("/food-order/update-category", methods=["POST", "GET"])
@login_required
@admin_only
def update_category():
    with app.app_context():
        category = Category.query.get(request.args.get("id"))
        if request.method == "POST":
            category.title = request.form.get("title")
            if not request.files.get("image").filename == "":
                category.image_name = request.files.get("image").filename
            category.featured = request.form.get("featured")
            category.active = request.form.get("active")
            db.session.commit()
            return redirect(url_for("manage_category"))
        return render_template("admin/update_category.html", category=category)


# Delete a category
@app.route("/food-order/delete-category")
@login_required
@admin_only
def delete_category():
    with app.app_context():
        category = Category.query.get(request.args.get("id"))
        db.session.delete(category)
        db.session.commit()
        return redirect(url_for("manage_category"))

# ############################## Manage Category section End ##########################################################
