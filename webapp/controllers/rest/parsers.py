from flask_restful import reqparse

user_post_parser = reqparse.RequestParser()
user_post_parser.add_argument('username', type=str, required=True)
user_post_parser.add_argument('password', type=str, required=True)

category_get_parser = reqparse.RequestParser()
category_get_parser.add_argument('page', type=int, location=['args', 'headers'])
category_get_parser.add_argument('user', type=str, location=['args', 'headers'])

category_post_parser = reqparse.RequestParser()
category_post_parser.add_argument(
    'token',
    type=str,
    required=True,
    help="Auth Token is required to edit posts"
)
category_post_parser.add_argument(
    'title',
    type=str,
    required=True,
    help="Title is required"
)
category_post_parser.add_argument(
    'text',
    type=str,
    required=True,
    help="Body text is required"
)
category_post_parser.add_argument(
    'tags',
    type=str,
    action='append'
)

category_put_parser = reqparse.RequestParser()
category_put_parser.add_argument(
    'token',
    type=str,
    required=True,
    help="Auth Token is required to create posts"
)
category_put_parser.add_argument(
    'title',
    type=str
)
category_put_parser.add_argument(
    'text',
    type=str
)
category_put_parser.add_argument(
    'tags',
    type=str
)

category_delete_parser = reqparse.RequestParser()
category_delete_parser.add_argument(
    'token',
    type=str,
    required=True,
    help="Auth Token is required to delete posts"
)
