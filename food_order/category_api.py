from flask_restful import Resource, fields, marshal_with, reqparse
from sqlalchemy.exc import IntegrityError

from food_order import api, db, Category, app

categories_args = reqparse.RequestParser()
categories_args.add_argument('title', required=False)
categories_args.add_argument('featured', required=False)
categories_args.add_argument('image', required=False)
categories_args.add_argument('active', required=False)

categories_field = {
    'id': fields.Integer,
    'title': fields.String,
    'image_name': fields.String,
    'featured': fields.String,
    'active': fields.String
}


class CategoriesApi(Resource):
    @marshal_with(categories_field)
    def get(self):
        with app.app_context():
            categories = db.session.query(Category).all()
            return categories

    @marshal_with(categories_field)
    def post(self):
        args = categories_args.parse_args()
        with app.app_context():
            try:
                new_category = Category(
                    title=args["title"],
                    image_name=args["image"],
                    featured=args["featured"],
                    active=args["active"],
                )
                db.session.add(new_category)
                db.session.commit()
                db.session.refresh(new_category)
            except IntegrityError as e:
                db.session.rollback()
                return {'message': e.detail}, 400
            return new_category, 201


class CategoryApi(Resource):
    @marshal_with(categories_field)
    def get(self, category_id):
        with (app.app_context()):
            category = Category.query.get(category_id)
            if category:
                return category, 200
            return category, 404

    @marshal_with(categories_field)
    def put(self, category_id):
        args = categories_args.parse_args()
        with (app.app_context()):
            category = Category.query.get(category_id)
            if category:
                try:
                    if args.get("title"):
                        category.title = args.get("title")
                    if args.get("image"):
                        category.image_name = args.get("image")
                    if args.get("featured"):
                        category.featured = args.get("featured")
                    if args.get('active'):
                        category.active = args.get("active")
                    db.session.add(category)
                    db.session.commit()
                    db.session.refresh(category)
                    return category, 200
                except IntegrityError as e:
                    db.session.rollback()
                    return {'message': e.detail}, 400
            return category, 404

    @marshal_with(categories_field)
    def delete(self, category_id):
        with app.app_context():
            category = Category.query.get(category_id)
            if category:
                db.session.delete(category)
                db.session.commit()
                return {"message": "Category deleted successfully"}, 204
            return category, 404


api.add_resource(CategoriesApi, '/api/category')
api.add_resource(CategoryApi, '/api/category/<category_id>')
