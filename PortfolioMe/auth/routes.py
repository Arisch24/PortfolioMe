from datetime import datetime
from flask import Blueprint, jsonify, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user
from PortfolioMe import db, bcrypt, mail
from PortfolioMe.models import Applicant
from PortfolioMe.auth.utils import send_admin_email, send_reset_email
from PortfolioMe.auth.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        list = form.ic.data.split("-")
        cleaned_ic = "".join(list)
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode("utf-8")  # decode - convert bytes to string
        applicant = Applicant(username=form.username.data, ic=cleaned_ic, mailing_address=form.mailing_address.data, password=hashed_password, gender=form.gender.data,
                              email=form.email.data, phone_number=form.phone_number.data)
        db.session.add(applicant)
        db.session.commit()
        flash(f"Your account has been created!", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        applicant = Applicant.query.filter_by(email=form.email.data).first()
        if applicant and bcrypt.check_password_hash(applicant.password, form.password.data):
            if applicant.status == "Active":
                applicant.last_active = datetime.utcnow()
                db.session.commit()
                login_user(applicant, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for("main.home"))
            elif applicant.status == "Inactive":
                flash("Your account has been blocked due to inactivity", "failed")
                return render_template("auth/login.html", form=form, button="Request Unblock")
            else:
                flash(
                    "Your account has been blocked by the admin due to suspicious behaviour", "failed")
                return render_template("auth/login.html", form=form, button="Request Unblock")
        else:
            flash(f"Login Unsuccessful! Check your email and password", "failed")

    return render_template("auth/login.html", form=form)


# AJAX API call
@auth.route("/request_unblock_account/<email>", methods=["GET"])
def request_unblock_account(email):
    applicant = Applicant.query.filter_by(email=email).first()
    send_admin_email(applicant, "Request Account Unblock",
                     "My account has been blocked. Can you kindly unblock it for me?")
    return jsonify({"status": "success"})


@auth.route("/reset_password", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RequestResetForm()
    if form.validate_on_submit():
        applicant = Applicant.query.filter_by(email=form.email.data).first()
        send_reset_email(applicant)
        flash("An email has been sent with instructions to reset your password", "info")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password_request.html", form=form)


@auth.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    applicant = Applicant.verify_reset_token(token)
    if applicant is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("auth.reset_password_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode("utf-8")  # decode - convert bytes to string
        applicant.password = hashed_password
        db.session.commit()
        flash(f"Your password has been reset! You are now able to login", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_token.html", form=form)


@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))
