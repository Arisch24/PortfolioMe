import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_session import Session
from flask_mail import Mail


app = Flask(__name__)
app.config["SECRET_KEY"] = "383ed93c7f5c33627fb4bf56036c7493"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config["FLASK_ADMIN_SWATCH"] = "sandstone"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"
session = Session(app)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("EMAIL_USER")
app.config["MAIL_PASSWORD"] = os.environ.get("EMAIL_PASSWORD")
mail = Mail(app)

from PortfolioMe.client.routes import client  # noqa
from PortfolioMe.auth.routes import auth  # noqa
from PortfolioMe.main.routes import main  # noqa

app.register_blueprint(client)
app.register_blueprint(auth)
app.register_blueprint(main)

from PortfolioMe import admin_routes  # noqa
