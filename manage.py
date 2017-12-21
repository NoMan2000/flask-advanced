from os import getenv

from flask_assets import ManageAssets
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Server
from flask_script.commands import ShowUrls, Clean

from utils.loadenvironment import load_environment
from webapp import create_app
from webapp.models import db, User, Role, Item, Category

load_environment()
# default to dev config
env = getenv('WEBAPP_ENV', 'dev')
app = create_app(f'webapp.config.{env.capitalize()}Config')

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command("server", Server())
manager.add_command("show-urls", ShowUrls())
manager.add_command("clean", Clean())
manager.add_command('db', MigrateCommand)
manager.add_command("assets", ManageAssets(env))


@manager.shell
def make_shell_context():
    return dict(
        app=app,
        db=db,
        User=User,
        Category=Category,
        Item=Item
    )


@manager.command
def setup_db():
    try:
        db.create_all()
        admin_role = Role('admin')
        admin_role.name = "admin"
        admin_role.description = "admin"
        db.session.add(admin_role)

        default_role = Role('default')
        default_role.name = "default"
        default_role.description = "default"
        db.session.add(default_role)

        admin = User('admin')
        admin.username = "admin"
        admin.set_password("password")
        admin.roles.append(admin_role)
        admin.roles.append(default_role)
        db.session.add(admin)
        db.session.commit()
    except:
        print("Already ran migration")
        pass


if __name__ == "__main__":
    manager.run()
