import datetime
from sqlalchemy import func, text
from flask import (render_template,
                   Blueprint,
                   redirect,
                   url_for,
                   request,
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
    recent = Category.query.order_by(
        Category.publish_date.desc()
    ).limit(5).all()

    top_items = db.session.query(Item).from_statement(
        text('''
        SELECT * FROM item
        JOIN category 
        ON item.category_id = category.id
    ''')).all()

    return recent, top_items


@blog_blueprint.route('/')
@blog_blueprint.route('/<int:page>')
@cache.cached(timeout=60)
def home(page=1):

    categories = Category.query.order_by(
        Category.publish_date.desc()
    ).paginate(page, 10, error_out=False)

    if categories.page != page:
        categories = Category.query.order_by(
            Category.publish_date.desc()
        ).paginate(1, 10, error_out=False)

    recent, top_items = sidebar_data()

    return render_template(
        'home.html',
        categories=categories,
        recent=recent,
        top_items=top_items
    )


@blog_blueprint.route('/category/<int:category_id>', methods=('GET', 'POST'))
@cache.cached(timeout=60)
def category(category_id):
    form = ItemForm()

    if form.validate_on_submit():
        new_category = Category(form.name.title)
        new_category.name = form.name.data
        new_category.text = form.text.data
        new_category.post_id = category_id
        new_category.date = datetime.datetime.now()

        db.session.add(new_category)
        db.session.commit()

    category = Category.query.get_or_404(category_id)
    items = Item.query.filter_by(category_id=category.id).all()
    recent, top_items = sidebar_data()

    return render_template(
        'category.html',
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
        new_post_model = Category(form.title.data)
        new_post_model.text = form.text.data
        new_post_model.publish_date = datetime.datetime.now()
        new_post_model.user = User.query.filter_by(
            username=current_user.username
        ).one()

        db.session.add(new_post_model)
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


@blog_blueprint.route('/item/<string:item_name>')
@cache.cached(timeout=60)
def item(item_name):
    item = Item.query.filter_by(name=item_name).first_or_404()
    categories = db.session.query(Category).from_statement(
        text(f'''
        SELECT * FROM category 
        WHERE id = {item.category_id}
    ''')).all()

    recent, top_items = sidebar_data()

    return render_template(
        'item.html',
        item=item,
        categories=categories,
        recent=recent,
        top_items=top_items
    )

@blog_blueprint.route('/item/')
@cache.cached(timeout=60)
def item_identifier():
    id = request.args.get('item_id')
    item = Item.query.get_or_404(id)
    categories = db.session.query(Category).from_statement(
        text(f'''
        SELECT * FROM category 
        WHERE id = {item.category_id}
    ''')).all()

    recent, top_items = sidebar_data()

    return render_template(
        'item.html',
        item=item,
        categories=categories,
        recent=recent,
        top_items=top_items
    )
