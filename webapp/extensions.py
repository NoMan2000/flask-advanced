from os import getenv

from flask import (
    flash,
    redirect,
    url_for,
    session
)
from flask_admin import Admin
from flask_assets import Environment, Bundle
from flask_bcrypt import Bcrypt
from flask_cache import Cache
from flask_celery import Celery
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_mail import Mail
from flask_oauth import OAuth
from flask_openid import OpenID
from flask_principal import Principal, Permission, RoleNeed
from flask_restful import Api

from utils.loadenvironment import load_environment

load_environment()
bcrypt = Bcrypt()
oid = OpenID()
oauth = OAuth()
principals = Principal()
rest_api = Api()
celery = Celery()
debug_toolbar = DebugToolbarExtension()
cache = Cache()
assets_env = Environment()
admin = Admin()
mail = Mail()

admin_permission = Permission(RoleNeed('admin'))
poster_permission = Permission(RoleNeed('poster'))
default_permission = Permission(RoleNeed('default'))

login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.session_protection = "strong"
login_manager.login_message = "Please login to access this page"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(userid):
    from webapp.models import User
    return User.query.get(userid)


@oid.after_login
def create_or_login(resp):
    from webapp.models import db, User
    username = resp.fullname or resp.nickname or resp.email

    if not username:
        flash('Invalid login. Please try again.', 'danger')
        return redirect(url_for('main.login'))

    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User(username)
        db.session.add(user)
        db.session.commit()

    session['username'] = username
    return redirect(url_for('blog.home'))


facebook = oauth.remote_app(
    'facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=getenv('FACEBOOK_CONSUMER_KEY'),
    consumer_secret=getenv('FACEBOOK_SECRET_KEY'),
    request_token_params={'scope': 'email'}
)

twitter = oauth.remote_app(
    'twitter',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    consumer_key=getenv('TWITTER_CONSUMER_KEY'),
    consumer_secret=getenv('TWITTER_CONSUMER_SECRET')
)


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('facebook_oauth_token')


@twitter.tokengetter
def get_twitter_oauth_token():
    return session.get('twitter_oauth_token')


main_css = Bundle(
    'css/bootstrap.css',
    filters='cssmin',
    output='css/common.css'
)

main_js = Bundle(
    'js/jquery.js',
    'js/popper.js',
    'js/bootstrap.js',
    filters='jsmin',
    output='js/common.js'
)
