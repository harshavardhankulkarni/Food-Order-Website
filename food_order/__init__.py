from functools import wraps

from flask import Flask, redirect, url_for, flash, abort
from flask_login import LoginManager, UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy

UPLOAD_FOLDER = "static/images/"
ALLOWED_EXTENSIONS = {"webp", "png", "jpg", "jpeg", "gif"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///food-order.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "secret_key"

# Create Database
db = SQLAlchemy(app, session_options={"autoflush": False})

# Login Management
login_manager = LoginManager(app)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# User Loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True)
    role = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    orders = db.relationship("Order", backref="customer")


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    image_name = db.Column(db.String(255), nullable=True)
    featured = db.Column(db.String(10), nullable=False)
    active = db.Column(db.String(10), nullable=False)
    foods = db.relationship("Food", backref="food")


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    image_name = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    featured = db.Column(db.String(10), nullable=False)
    active = db.Column(db.String(10), nullable=False)
    orders = db.relationship("Order", backref="order")


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_id = db.Column(db.Integer, db.ForeignKey("food.id"))
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    qty = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)
    order_date = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    customer_name = db.Column(db.String(150), nullable=False)
    customer_contact = db.Column(db.String(20), nullable=False)
    customer_email = db.Column(db.String(150), nullable=False)
    customer_address = db.Column(db.String(255), nullable=False)


# Create tables
with app.app_context():
    db.create_all()


# Admin decorator
def admin_only(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            if current_user.role == "admin":
                return f(*args, **kwargs)
            else:
                abort(403)
        else:
            return redirect(url_for("admin_index"))

    return wrapper


def login_required_for_customer(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            return f(*args, **kwargs)
        else:
            flash("Login required")
            return redirect(url_for("login"))

    return wrapper


def super_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            if current_user.role == "admin" and current_user.id == 1:
                return f(*args, **kwargs)
            else:
                abort(403)
        else:
            return redirect(url_for("admin_index"))

    return wrapper


from food_order import admin, views, customer, category, food, order
