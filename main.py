import sys

from werkzeug.security import generate_password_hash

from food_order import app, Admin, db

if __name__ == "__main__":
    args = sys.argv

    if len(args) > 1:
        if args[1] == 'createsuperuser':
            full_name = input('Full Name: ')
            username = input("Username: ")
            password = input("Password: ")
            with app.app_context():
                super_admin = Admin(
                    full_name=full_name,
                    username=username,
                    password=generate_password_hash(password, salt_length=8),
                    role="admin",
                )
                db.session.add(super_admin)
                db.session.commit()
    else:
        app.run(debug=True)
