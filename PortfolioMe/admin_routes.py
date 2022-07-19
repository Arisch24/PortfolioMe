import os
import secrets
from datetime import datetime
from flask import render_template, session, redirect, url_for, request, flash, abort, current_app
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, Admin, expose, BaseView, form
from flask_login import current_user
from PortfolioMe import models, bcrypt, db, admin
from PortfolioMe.models import Resume
from PortfolioMe.admin_forms import AdminEditResumeForm, AdminLoginForm
from wtforms import PasswordField
from wtforms.validators import DataRequired

resume_path = os.path.join(os.path.dirname(__file__), 'static\\resumes')
job_board_path = os.path.join(os.path.dirname(__file__), 'static\\jobs')


def filename_generation(obj, file_data):
    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(file_data.filename)
    new_filename = random_hex + file_extension
    return new_filename


class ApplicantView(ModelView):
    '''This view is for admin to view all the tables in the database'''

    form_excluded_columns = ("password")

    form_extra_fields = {
        "new_password": PasswordField("New Password")
    }

    form_columns = (
        "username",
        "new_password",
        "gender",
        "email",
        "phone_number",
        "organization",
        "resumes_owned"
    )

    column_searchable_list = ["username",
                              "email", "phone_number", "organization"]

    def on_model_change(self, form, model, is_created):
        if form.new_password.data != '':
            model.password = bcrypt.generate_password_hash(
                form.new_password.data).decode("utf-8")

    # Custom filters
    can_view_details = True
    can_export = True
    can_set_page_size = True

    create_template = "custom/create.html"
    edit_template = "custom/edit.html"
    details_template = "custom/details.html"
    list_template = "custom/list.html"

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
                return redirect(url_for("auth.login"))


class ResumeView(BaseView):
    '''This view is same as other views but allows file uploading'''

    @expose("/", methods=["GET", "POST"])
    def resumes(self):
        page = request.args.get('page', 1, type=int)
        resumes = Resume.query.order_by(
            Resume.id.asc()).paginate(page=page, per_page=5)
        return self.render("custom/resume/home_resume.html", resumes=resumes)

    @expose("/edit/<int:resume_id>", methods=["GET", "POST"])
    def edit_resume(self, resume_id):
        resume = Resume.query.get_or_404(resume_id)
        form = AdminEditResumeForm()
        if form.validate_on_submit():
            # save the edited resume
            resume.applicant_details = form.applicant_details.data
            resume.is_bookmarked = form.is_bookmarked.data
            resume.is_hired = form.is_hired.data
            resume.date_edited = datetime.utcnow()
            db.session.commit()
            flash("Resume has been edited successfully", "success")
            return redirect(url_for("resumes.resumes"))
        elif request.method == "GET":
            form.applicant_details.data = resume.applicant_details
            form.is_bookmarked.data = resume.is_bookmarked
            form.is_hired.data = resume.is_hired
        return self.render("custom/resume/edit_resume.html", resume=resume, form=form)

    @expose("/details/<int:resume_id>", methods=["GET", "POST"])
    def details_resume(self, resume_id):
        resume = Resume.query.get_or_404(resume_id)
        return self.render("custom/resume/details_resume.html", resume=resume)

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
                return redirect(url_for("auth.login"))


class JobBoardView(ModelView):
    '''This view is same as other views but allows file uploading'''

    form_extra_fields = {
        'image': form.FileUploadField(label='Upload Image Here',
                                      validators=[DataRequired()],
                                      base_path=job_board_path,
                                      namegen=filename_generation, allowed_extensions=['png', 'jpg', 'jpeg'], allow_overwrite=True),
    }

    column_searchable_list = ["name", "description",
                              "department", "salary", "job_type"]

    def on_model_change(self, form, model, is_created):
        model.job_image = model.image

    def on_model_delete(self, model):
        os.remove(job_board_path + f"\{model.job_image}")

    # Custom filters
    can_view_details = True
    can_export = True
    can_set_page_size = True

    create_template = "custom/create.html"
    edit_template = "custom/edit.html"
    details_template = "custom/details.html"
    list_template = "custom/list.html"

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
                return redirect(url_for("auth.login"))


class InsightsView(ModelView):
    '''This view is for admin to view all the tables in the database'''

    # Custom filters
    can_view_details = True
    can_export = True
    can_set_page_size = True

    create_template = "custom/create.html"
    edit_template = "custom/edit.html"
    details_template = "custom/details.html"
    list_template = "custom/list.html"

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
                return redirect(url_for("auth.login"))


class HomeAdminView(AdminIndexView):
    '''This view is for anyone accessing the admin page'''

    @expose('/')
    def index(self):
        if not session.get("admin"):
            return redirect(url_for('.admin_login'))
        return super(HomeAdminView, self).index()

    @expose('/login', methods=['GET', 'POST'])
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


class ManageAdminView(ModelView):
    '''This is the manage admin view'''

    form_excluded_columns = ("password")

    form_extra_fields = {
        "new_password": PasswordField("New Password")
    }

    form_columns = (
        "username",
        "new_password",
        "gender",
    )

    column_searchable_list = ["username", "gender"]

    def on_model_change(self, form, model, is_created):
        if form.new_password.data != '':
            model.password = bcrypt.generate_password_hash(
                form.new_password.data).decode("utf-8")

    # Custom filters
    can_view_details = True
    can_export = True
    can_set_page_size = True

    create_template = "custom/create.html"
    edit_template = "custom/edit.html"
    details_template = "custom/details.html"
    list_template = "custom/list.html"

    def is_accessible(self):
        if session.get("admin") and session.get("admin").id == 1:
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
                return redirect(url_for("auth.login"))


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
admin._set_admin_index_view(index_view=HomeAdminView())
admin.base_template = "admin/base.html"
admin.name = "PortfolioMe"
admin.template_mode = "bootstrap4"
admin.add_view(ApplicantView(models.Applicant, db.session))
admin.add_view(ResumeView(name="Resumes", endpoint="resumes"))
admin.add_view(JobBoardView(models.JobBoard, db.session))
admin.add_view(InsightsView(models.Insights, db.session))
admin.add_view(ManageAdminView(models.Admin, db.session,
               name="Manage Admin", endpoint="manage_admin"))
admin.add_view(LogoutAdminView(name="Logout", endpoint="logout"))
