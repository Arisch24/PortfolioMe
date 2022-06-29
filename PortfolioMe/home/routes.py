from flask import Blueprint, render_template

home = Blueprint("home", __name__)


@home.route("/")
@home.route("/index")
@home.route("/home")
def home():
    return render_template("client/index.html")
