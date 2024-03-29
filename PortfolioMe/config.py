import os
from dotenv import load_dotenv
from os.path import join, dirname

dotenv_path = join(dirname(__file__), '.env')

load_dotenv(dotenv_path=dotenv_path, override=True)


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    FLASK_ADMIN_SWATCH = "litera"
    FLASK_ADMIN_FLUID_LAYOUT = True
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"
    REMEMBER_COOKIE_DURATION = 604800
    REMEMBER_COOKIE_REFRESH_EACH_REQUEST = True
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("EMAIL_USER")
    MAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
