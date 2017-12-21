import tempfile
from os import getenv

from celery.schedules import crontab

from utils.loadenvironment import load_environment

load_environment()


class Config(object):
    SECRET_KEY = getenv('CELERY_SECRET_KEY')
    RECAPTCHA_PUBLIC_KEY = getenv('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = getenv('RECAPTCHA_PRIVATE_KEY')
    secret_key = getenv('SECRET_KEY')
    CELERYBEAT_SCHEDULE = {
        'weekly-digest': {
            'task': 'tasks.digest',
            'schedule': crontab(day_of_week=6, hour='10')
        },
    }
    CELERY_BROKER_URL = "amqp://guest:guest@localhost:5672//"
    CELERY_BACKEND_URL = "amqp://guest:guest@localhost:5672//"

    MAIL_SERVER = getenv('MAIL_SERVER', 'localhost')
    MAIL_PORT = getenv('MAIL_PORT', 25)
    MAIL_USERNAME = getenv('MAIL_USERNAME')
    MAIL_PASSWORD = getenv('MAIL_PASSWORD')


class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = getenv('SQLALCHEMY_DATABASE_URI')
    CACHE_TYPE = 'simple'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(Config):
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    ASSETS_DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'sqlite:///../items.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CACHE_TYPE = 'null'
    CACHE_NO_NULL_WARNING = True


class TestConfig(Config):
    db_file = tempfile.NamedTemporaryFile()

    DEBUG = True
    DEBUG_TB_ENABLED = False

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + db_file.name
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = 'null'
    CACHE_NO_NULL_WARNING = True
    WTF_CSRF_ENABLED = False
