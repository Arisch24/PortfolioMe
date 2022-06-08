import re
from flask import redirect, url_for, render_template, request, flash
from PortfolioMe import app, db, bcrypt
from PortfolioMe.forms import EditProfileForm, RegistrationForm, LoginForm, ResumeSubmissionForm
from PortfolioMe.models import Applicant, Admin, Resume, JobBoard, Insights
from flask_login import login_user, current_user, logout_user, login_required

# Client routes
@app.route("/")
@app.route("/index")
@app.route("/home")
def home():
    return render_template("client/index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8") # decode - convert bytes to string
        applicant = Applicant(username=form.username.data, password=hashed_password, gender=form.gender.data, email=form.email.data, phone_number=form.phone_number.data, organization=form.organization.data)
        db.session.add(applicant)
        db.session.commit()
        flash(f"Your account has been created!", "success")
        return redirect(url_for("login"))

    return render_template("auth/register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        applicant = Applicant.query.filter_by(email=form.email.data).first()
        if applicant and bcrypt.check_password_hash(applicant.password, form.password.data):
            login_user(applicant, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash(f"Login Unsuccessful! Check your email and password", "failed")

    return render_template("auth/login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/account")
@login_required
def account():
    return render_template("client/account.html")


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        flash(f"Profile updated successfully.", "success")
    return render_template("client/edit_profile.html", form=form)


@app.route("/job_board")
@login_required
def job_board():
    return render_template("client/job_board.html")


@app.route("/upload_resume", methods=["GET", "POST"])
@login_required
def upload_resume():
    form = ResumeSubmissionForm()
    if request.method == "GET":
        return render_template("client/upload_resume.html", form=form)




# Admin routes
