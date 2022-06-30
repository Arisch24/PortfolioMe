from flask import Blueprint, render_template

main = Blueprint("main", __name__)


@main.route("/")
@main.route("/index")
@main.route("/home")
def home():
    return render_template("main/index.html")
