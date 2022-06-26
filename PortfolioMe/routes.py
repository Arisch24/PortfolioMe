import os
import secrets
from PIL import Image
from flask import abort, redirect, url_for, render_template, request, flash, session
from PortfolioMe import app, db, bcrypt
from PortfolioMe.forms import EditProfileForm, RegistrationForm, LoginForm, ResumeSubmissionForm, AdminLoginForm
from PortfolioMe.models import Applicant, Resume, JobBoard, Insights
from PortfolioMe import models
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, Admin, expose, BaseView, helpers
from flask_login import login_user, current_user, logout_user, login_required

'''
=============================================================
                        Applicant Section
=============================================================
'''


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
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode("utf-8")  # decode - convert bytes to string
        applicant = Applicant(username=form.username.data, password=hashed_password, gender=form.gender.data,
                              email=form.email.data, phone_number=form.phone_number.data, organization=form.organization.data)
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


@app.route("/forgot_password")
def forgot_password():
    return render_template("client/forgot_password.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.phone_number = form.phone_number.data
        current_user.gender = form.gender.data
        current_user.organization = form.organization.data
        db.session.commit()
        flash(f"Profile updated successfully.", "success")
        return redirect(url_for("edit_profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone_number.data = current_user.phone_number
        form.gender.data = current_user.gender
        form.organization.data = current_user.organization
    return render_template("client/edit_profile.html", form=form)


@app.route("/job_board")
@login_required
def job_board():
    jobs = JobBoard.query.all()
    return render_template("client/job_board.html", jobs=jobs)


@app.route("/job_board/<int:job_id>")
@login_required
def job_detail(job_id):
    job = JobBoard.query.get_or_404(job_id)
    return render_template("client/job_detail.html", job=job)


@app.route("/job_board/<int:job_id>/upload_resume")
@login_required
def upload_resume(job_id):
    job = JobBoard.query.get_or_404(job_id)
    form = ResumeSubmissionForm()
    return render_template("client/upload_resume.html", form=form)


# Function to save the resume image
def save_resume(form_resume):
    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(form_resume.filename)
    resume_name = random_hex + file_extension
    resume_path = os.path.join(app.root_path, 'static/resumes', resume_name)

    # Resizing image
    output_size = (1080, 1920)  # size of image
    image = Image.open(form_resume)
    image.thumbnail(output_size)
    image.save(resume_path)

    return resume_name


@app.route("/resume_list")
@login_required
def resume_list():
    return render_template("client/resume_list.html")


'''
=============================================================
                        Admin Section
=============================================================
'''


class DatabaseView(ModelView):
    '''This view is for admin to view all the tables in the database'''

    def is_accessible(self):
        if session.get("admin"):
            return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for(".admin_login", next=request.url))

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
                flash("You are not allowed to access this page", "failed")
                return redirect(url_for("login"))


class HomeAdminView(AdminIndexView):
    '''This view is for anyone accessing the admin page'''

    @expose('/')
    def index(self):
        if not session.get("admin"):
            return redirect(url_for('.admin_login'))
        return super(HomeAdminView, self).index()

    @expose('/login', methods=('GET', 'POST'))
    def admin_login(self):
        # handle user login
        form = AdminLoginForm()
        if form.validate_on_submit():
            admin = models.Admin.query.filter_by(
                username=form.username.data).first()
            if admin and bcrypt.check_password_hash(admin.password, form.password.data):
                session["admin"] = admin
                return redirect("/admin")
            else:
                flash(f"Check your username and password", "failed")
        return self.render("admin/login.html", form=form)


class ManageAdminView(BaseView):
    '''This is the manage admin view'''

    @expose("/", methods=["GET", "POST"])
    def manage_admin(self):
        return self.render("admin/manage_admin.html")

    def is_accessible(self):
        if session.get("admin"):
            return True
        return False


class LogoutAdminView(BaseView):
    '''This is the logout view'''

    @expose("/", methods=["GET", "POST"])
    def logout(self):
        session.pop("admin")
        return redirect("/admin")

    def is_accessible(self):
        if session.get("admin"):
            return True
        return False


# Admin Views
admin = Admin(app, name="PortfolioMe", index_view=HomeAdminView(),
              base_template="admin/base.html")
admin.add_view(DatabaseView(Applicant, db.session))
admin.add_view(DatabaseView(Resume, db.session))
admin.add_view(DatabaseView(JobBoard, db.session))
admin.add_view(DatabaseView(Insights, db.session))
admin.add_view(ManageAdminView(name="Manage Admin", endpoint="manage_admin"))
admin.add_view(LogoutAdminView(name="Logout", endpoint="logout"))
