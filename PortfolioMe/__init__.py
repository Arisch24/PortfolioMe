import atexit
from datetime import datetime
from email.mime import application
from dateutil.relativedelta import relativedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_session import Session
from flask_mail import Mail
from flask_admin import Admin
from flask_apscheduler import APScheduler
from PortfolioMe.config import Config


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"
session = Session()
mail = Mail()
admin = Admin()
scheduler = APScheduler()

from PortfolioMe import admin_routes, models  # noqa


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    with app.app_context():
        db.init_app(app)
        bcrypt.init_app(app)
        login_manager.init_app(app)
        session.init_app(app)
        mail.init_app(app)
        admin.init_app(app)
        scheduler.init_app(app)
        scheduler.start()

        from PortfolioMe.client.routes import client  # noqa
        from PortfolioMe.auth.routes import auth  # noqa
        from PortfolioMe.main.routes import main  # noqa
        from PortfolioMe.errors.handlers import errors  # noqa

        app.register_blueprint(client)
        app.register_blueprint(auth)
        app.register_blueprint(main)
        app.register_blueprint(errors)

    def check_inactive_users():
        with app.app_context():
            today_date = datetime.utcnow() - relativedelta(months=+3)
            applicants = models.Applicant.query.filter(
                models.Applicant.last_active < today_date).all()
            if applicants:
                for applicant in applicants:
                    applicant.status = "Inactive"
                db.session.commit()

    job = scheduler.add_job(id='1234', func=check_inactive_users,
                            trigger='cron', minute="0", hour="2", day="*", month="*")

    atexit.register(lambda: scheduler.shutdown(wait=True))

    return app
