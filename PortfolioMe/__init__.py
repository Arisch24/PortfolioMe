from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_session import Session

app = Flask(__name__)
app.config["SECRET_KEY"] = "383ed93c7f5c33627fb4bf56036c7493"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config["FLASK_ADMIN_SWATCH"] = "sandstone"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"
session = Session(app)

from PortfolioMe import routes