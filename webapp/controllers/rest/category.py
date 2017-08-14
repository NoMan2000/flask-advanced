import datetime

from flask import abort
from flask_restful import Resource, fields, marshal_with

from webapp.models import db, User, Category, Item
from .parsers import (
    category_get_parser,
    category_post_parser,
    category_put_parser,
    category_delete_parser
)
from .fields import HTMLField


nested_tag_fields = {
    'id': fields.Integer(),
    'title': fields.String()
}

category_fields = {
    'id': fields.Integer(),
    'author': fields.String(attribute=lambda x: x.user.username),
    'title': fields.String(),
    'text': HTMLField(),
    'tags': fields.List(fields.Nested(nested_tag_fields)),
    'publish_date': fields.DateTime(dt_format='iso8601')
}


class CategoryApi(Resource):
    @marshal_with(category_fields)
    def get(self, category_id=None):
        if category_id:
            category = Category.query.get(category_id)
            if not category:
                abort(404)

            return category
        else:
            args = category_get_parser.parse_args()
            page = args['page'] or 1

            if args['user']:
                user = User.query.filter_by(username=args['user']).first()
                if not user:
                    abort(404)

                categories = user.categories.order_by(
                    Category.publish_date.desc()
                ).paginate(page, 30)
            else:
                categories = Category.query.order_by(
                    Category.publish_date.desc()
                ).paginate(page, 30)

            return categories.items

    def post(self, category_id=None):
        if category_id:
            abort(400)
        else:
            args = category_post_parser.parse_args(strict=True)

            user = User.verify_auth_token(args['token'])
            if not user:
                abort(401)

            new_post = Category(args['title'])
            new_post.user = user
            new_post.date = datetime.datetime.now()
            new_post.text = args['text']

            if args['items']:
                for item in args['items']:
                    tag = Item.query.filter_by(title=item).first()

                    # Add the tag if it exists. If not, make a new tag
                    if tag:
                        new_post.tags.append(tag)
                    else:
                        new_tag = Item(item)
                        new_post.tags.append(new_tag)

            db.session.add(new_post)
            db.session.commit()
            return new_post.id, 201

    def put(self, category_id=None):
        if not category_id:
            abort(400)

        post = Category.query.get(category_id)
        if not post:
            abort(404)

        args = category_put_parser.parse_args(strict=True)
        user = User.verify_auth_token(args['token'])
        if not user:
            abort(401)
        if user != post.user:
            abort(403)

        if args['title']:
            post.title = args['title']

        if args['text']:
            post.text = args['text']

        if args['items']:
            for item in args['items']:
                tag = Item.query.filter_by(title=item).first()

                # Add the tag if it exists. If not, make a new tag
                if tag:
                    post.tags.append(tag)
                else:
                    new_tag = Item(item)
                    post.tags.append(new_tag)

        db.session.add(post)
        db.session.commit()
        return post.id, 201

    def delete(self, category_id=None):
        if not category_id:
            abort(400)

        post = Category.query.get(category_id)
        if not post:
            abort(404)

        args = category_delete_parser.parse_args(strict=True)
        user = User.verify_auth_token(args['token'])
        if user != post.user:
            abort(401)

        db.session.delete(post)
        db.session.commit()
        return "", 204
