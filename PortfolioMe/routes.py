from flask import redirect, url_for, render_template, request, flash
from PortfolioMe import app
from PortfolioMe.forms import EditProfileForm, RegistrationForm, LoginForm
from PortfolioMe.models import Applicant, Admin, Resume, JobBoard, Insights

# Client routes
@app.route("/")
@app.route("/index")
def home():
    return render_template("client/index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if(request.method == "POST"):
        if form.validate_on_submit():
            flash(f"Account created for {form.username.data}!", "success")
        else:
            flash(f"Your data is invalid. Try again.", "failed")

    return render_template("auth/register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if(request.method == "POST"):
        if form.validate_on_submit():
            if form.email.data == 'admin@admin.com' and form.password.data == 'password':
                flash(f"Successful login!", "success")
                return redirect(url_for("home"))
            else:
                flash(f"Login Unsuccessful!", 'failed')
    return render_template("auth/login.html", form=form)


@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    form = EditProfileForm()
    if(request.method == "POST"):
        if form.validate_on_submit():
            flash(f"Profile updated successfully.", "success")
        else:
            flash(f"There were some errors.", "failure")
    return render_template("client/edit_profile.html", form=form)

@app.route("/job_board")
def job_board():
    return render_template("client/job_board.html")

@app.route("/upload_resume", methods=["GET, POST"])
def upload_resume():
    return render_template("upload_resume.html")

# Admin routes
