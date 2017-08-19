import os
import datetime
import random
from flask_assets import ManageAssets
from flask_script import Manager, Server
from flask_script.commands import ShowUrls, Clean
from flask_migrate import Migrate, MigrateCommand
from webapp import create_app
from webapp.models import db, User, Role, Item, Category

# default to dev config
env = os.environ.get('WEBAPP_ENV', 'dev')
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

    s = "Body text"

    db.session.commit()


if __name__ == "__main__":
    manager.run()
