import os
import secrets
from flask import (session, redirect, url_for, request, flash, abort, Markup,
                   jsonify, current_app)
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, Admin, expose, BaseView, form
from flask_login import current_user
from PortfolioMe import models, bcrypt, db, admin, scheduler
from PortfolioMe.constants import (
    account_status, resume_status, job_types, department_types, position_level, experience_in_years, specialization_in)
from PortfolioMe.admin_forms import AdminLoginForm
from wtforms import PasswordField, SelectField
from wtforms.validators import DataRequired, Length

resume_path = os.path.join(os.path.dirname(__file__), 'static\\resumes')
job_board_path = os.path.join(os.path.dirname(__file__), 'static\\jobs')


def filename_generation(obj, file_data):
    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(file_data.filename)
    new_filename = random_hex + file_extension
    return new_filename


class ApplicantView(ModelView):
    '''This view is for admin to view all the tables in the database'''

    column_exclude_list = ("password")

    def status_formatter(view, context, model, name):
        status = []
        for i in range(len(account_status)):
            if model.status == account_status[i]:
                status.append(
                    f'<option value="{account_status[i]}" selected>{account_status[i]}</option>')
            else:
                status.append(
                    f'<option value="{account_status[i]}">{account_status[i]}</option>')
        return Markup(f'<label for="status"></label><select class="form-control status-select" id="status" name="{model.id}">{status}</select>')

    column_formatters = {
        'status': status_formatter
    }

    form_excluded_columns = ("password")

    form_extra_fields = {
        "new_password": PasswordField("New Password", validators=[Length(
            min=8, message="Minimum length is %(min)d characters.")])
    }

    form_columns = (
        "username",
        "ic",
        "mailing_address",
        "new_password",
        "gender",
        "email",
        "phone_number",
        "resumes_owned"
    )

    column_searchable_list = ["username",
                              "email", "phone_number"]

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

    # AJAX request
    @expose("/update_status", methods=["GET", "POST"])
    def update_status(self):
        if request.method == "POST":
            id = request.json['id']
            status = request.json['status']
            applicant = models.Applicant.query.filter_by(id=id).first()
            applicant.status = status
            db.session.commit()
            return jsonify({"status": "success", "applicant_status": status})
        return jsonify({"request": "no function"})

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


class ResumeView(ModelView):
    '''This view is same as other views but allows file uploading'''

    def resume_image_formatter(view, context, model, name):
        return Markup(f'<a class="resume-image" target="_blank" href="{ url_for("static", filename="resumes/" + model.image) }">resume.pdf</a>')

    column_formatters = {
        'image': resume_image_formatter
    }

    form_excluded_columns = ("resume_details_ref")

    def status_formatter(view, context, model, name):
        status = []
        for i in range(len(resume_status)):
            if model.status == resume_status[i]:
                status.append(
                    f'<option value="{resume_status[i]}" selected>{resume_status[i]}</option>')
            else:
                status.append(
                    f'<option value="{resume_status[i]}">{resume_status[i]}</option>')
        return Markup(f'<label for="status"></label><select class="form-control status-select" id="status" name="{model.id}">{status}</select>')

    column_formatters = {
        'status': status_formatter
    }

    form_extra_fields = {
        'old_image': form.Select2TagsField(label='Old image name',
                                           validators=None),
        'resume_image': form.FileUploadField(label='Upload Resume Image Here',
                                             validators=None,
                                             base_path=resume_path,
                                             namegen=filename_generation, allowed_extensions=['pdf'], allow_overwrite=True),
    }

    form_widget_args = {
        'image': {
            'readonly': True,
            'placeholder': 'This is readonly upload your file below.'
        },
        'old_image': {
            'disabled': True,
            'placeholder': 'Disabled field.'
        }
    }

    column_searchable_list = ["applicant_details", "date_edited", "status"]

    column_exclude_list = ("applicant_details")

    def on_model_change(self, form, model, is_created):
        model.image = model.resume_image

    def on_model_delete(self, model):
        os.remove(resume_path + f"\{model.image}")
        documents = model.additional_documents.split("-")
        for doc in documents:
            os.remove(resume_path + f"\{doc}")
        resume_details = models.Resume_Details.query.filter_by(
            id=model.resume_details_ref.id).delete()
        db.session.commit()

    # Custom filters
    can_create = False
    can_edit = False
    can_view_details = True
    can_export = True
    can_set_page_size = True

    create_template = "custom/create.html"
    edit_template = "custom/edit.html"
    details_template = "custom/details.html"
    list_template = "custom/list.html"

    # AJAX request
    @expose("/update_status", methods=["GET", "POST"])
    def update_status(self):
        if request.method == "POST":
            id = request.json['id']
            status = request.json['status']
            resume = models.Resume.query.filter_by(id=id).first()
            resume.status = status
            db.session.commit()
            return jsonify({"status": "success", "resume_status": status})
        return jsonify({"request": "no function"})

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


class ResumeDetailsView(ModelView):
    '''This view is for resume details'''

    column_exclude_list = ("mailing_address", "education", "skills", "soft_skills",
                           "work_experience", "associated_resume")

    # Custom filters
    can_create = False
    can_edit = False
    can_delete = False
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


class JobBoardView(ModelView):
    '''This view is same as other views but allows file uploading'''

    column_exclude_list = ("highlights", "description")

    form_extra_fields = {
        'old_image': form.Select2TagsField(label='Old image name',
                                           validators=None),
        'image': form.FileUploadField(label='Upload Image Here',
                                      validators=None,
                                      base_path=job_board_path,
                                      namegen=filename_generation, allowed_extensions=['png', 'jpg', 'jpeg', 'webp'], allow_overwrite=True),
    }

    form_widget_args = {
        'job_image': {
            'readonly': True,
            'placeholder': 'This is readonly upload your file below.'
        },
        'old_image': {
            'readonly': True,
            'placeholder': 'Readonly field.'
        }
    }

    form_args = dict(
        department=dict(label='Department', validators=[
                        DataRequired()], choices=department_types),
        job_type=dict(label='Job Type', validators=[
                      DataRequired()], choices=job_types),
        position_level=dict(label='Position Level', validators=[
                            DataRequired()], choices=position_level),
        years_of_experience=dict(label='Years Of Experience', validators=[
                                 DataRequired()], choices=experience_in_years),
        specializations=dict(label='Specializations', validators=[
                             DataRequired()], choices=specialization_in)
    )

    form_overrides = dict(department=SelectField,
                          job_type=SelectField, position_level=SelectField, years_of_experience=SelectField, specializations=SelectField)

    column_searchable_list = ["name", "description",
                              "department", "job_type"]

    def on_model_change(self, form, model, is_created):
        if not is_created:
            if form.old_image.data != "":
                os.remove(job_board_path + f"\{form.old_image.data}")
                model.job_image = model.image
        else:
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
admin.add_view(ApplicantView(models.Applicant,
               db.session, name="Registered Users"))
admin.add_view(ResumeView(models.Resume, db.session, name="Sent Resumes"))
admin.add_view(ResumeDetailsView(models.Resume_Details,
               db.session, name="Resume Details Forms"))
admin.add_view(JobBoardView(models.JobBoard, db.session, name="Edit Jobs"))
admin.add_view(InsightsView(models.Insights, db.session, name="View Insights"))
admin.add_view(ManageAdminView(models.Admin, db.session,
               name="Manage Admin", endpoint="manage_admin"))
admin.add_view(LogoutAdminView(name="Logout", endpoint="logout"))
