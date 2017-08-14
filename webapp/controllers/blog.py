import datetime
from sqlalchemy import func
from flask import (render_template,
                   Blueprint,
                   redirect,
                   url_for,
                   abort)
from flask_login import login_required, current_user
from flask_principal import Permission, UserNeed

from webapp.extensions import poster_permission, admin_permission, cache
from webapp.models import db, User, Item, Category
from webapp.forms import ItemForm, CategoryForm

blog_blueprint = Blueprint(
    'blog',
    __name__,
    template_folder='../templates/blog',
    url_prefix="/blog"
)


@cache.cached(timeout=7200, key_prefix='sidebar_data')
def sidebar_data():
    recent = Category.query.order_by(Category.publish_date.desc()).limit(5).all()
    items = recent.items
    top_items = db.session.query(
        Item, func.count(items).label('total')
    ).join(items).group_by(Item).order_by('total DESC').limit(5).all()

    return recent, top_items


@blog_blueprint.route('/')
@blog_blueprint.route('/<int:page>')
@cache.cached(timeout=60)
def home(page=1):
    categories = Category.query.order_by(Category.publish_date.desc()).paginate(page, 10)
    recent, top_items = sidebar_data()

    return render_template(
        'home.html',
        categories=categories,
        recent=recent,
        top_items=top_items
    )


@blog_blueprint.route('/categories/<int:category_id>', methods=('GET', 'POST'))
@cache.cached(timeout=60)
def post(category_id):
    form = ItemForm()

    if form.validate_on_submit():
        new_comment = Comment()
        new_comment.name = form.name.data
        new_comment.text = form.text.data
        new_comment.post_id = category_id
        new_comment.date = datetime.datetime.now()

        db.session.add(new_comment)
        db.session.commit()

    category = Category.query.get_or_404(category_id)
    items = category_id.items
    comments = category.comments.order_by(Item.date.desc()).all()
    recent, top_items = sidebar_data()

    return render_template(
        'post.html',
        category=category,
        recent=recent,
        top_items=top_items,
        form=form
    )


@blog_blueprint.route('/new', methods=['GET', 'POST'])
@login_required
@poster_permission.require(http_exception=403)
def new_post():
    form = CategoryForm()

    if form.validate_on_submit():
        new_post = Category(form.title.data)
        new_post.text = form.text.data
        new_post.publish_date = datetime.datetime.now()
        new_post.user = User.query.filter_by(
            username=current_user.username
        ).one()

        db.session.add(new_post)
        db.session.commit()

    return render_template('new.html', form=form)


@blog_blueprint.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@poster_permission.require(http_exception=403)
def edit_post(id):
    post = Category.query.get_or_404(id)

    permission = Permission(UserNeed(post.user.id))

    # We want admins to be able to edit any post
    if permission.can() or admin_permission.can():
        form = CategoryForm()

        if form.validate_on_submit():
            post.title = form.title.data
            post.text = form.text.data
            post.publish_date = datetime.datetime.now()

            db.session.add(post)
            db.session.commit()

            return redirect(url_for('.post', post_id=post.id))

        form.text.data = post.text

        return render_template('edit.html', form=form, post=post)

    abort(403)


@blog_blueprint.route('/tag/<string:tag_name>')
@cache.cached(timeout=60)
def tag(tag_name):
    item = Item.query.filter_by(title=tag_name).first_or_404()
    posts = tag.posts.order_by(Category.publish_date.desc()).all()
    recent, top_items = sidebar_data()

    return render_template(
        'tag.html',
        tag=tag,
        posts=posts,
        recent=recent,
        top_items=top_items
    )


@blog_blueprint.route('/user/<string:username>')
@cache.cached(timeout=60)
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Category.publish_date.desc()).all()
    recent, top_items = sidebar_data()

    return render_template(
        'user.html',
        user=user,
        posts=posts,
        recent=recent,
        top_items=top_items
    )
