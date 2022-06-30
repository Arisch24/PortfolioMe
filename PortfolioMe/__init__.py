from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_session import Session
from flask_mail import Mail
from flask_admin import Admin
from PortfolioMe.config import Config


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"
session = Session()
mail = Mail()
admin = Admin()


from PortfolioMe import admin_routes  # noqa


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    session.init_app(app)
    mail.init_app(app)
    admin.init_app(app)

    from PortfolioMe.client.routes import client  # noqa
    from PortfolioMe.auth.routes import auth  # noqa
    from PortfolioMe.main.routes import main  # noqa
    from PortfolioMe.errors.handlers import errors  # noqa

    app.register_blueprint(client)
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app
