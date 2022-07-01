
from ast import Mod
from flask import Blueprint, session, redirect, url_for, request, flash, abort, current_app
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, Admin, expose, BaseView, form
from flask_login import current_user
from PortfolioMe import models, bcrypt, db, admin
from PortfolioMe.admin_forms import AdminLoginForm
from wtforms import StringField


class ApplicantView(ModelView):
    '''This view is for admin to view all the tables in the database'''

    # Custom filters
    can_view_details = True
    can_export = True
    can_set_page_size = True

    create_template = "custom/create.html"
    edit_template = "custom/edit.html"
    details_template = "custom/details.html"
    list_template = "custom/list.html"

    def scaffold_form(self):
        form_class = super(ApplicantView, self).scaffold_form()
        form_class.extra = StringField('Extra')
        return form_class

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
    '''This view is for admin to view all the tables in the database'''

    # Custom filters
    can_view_details = True
    can_export = True
    can_set_page_size = True

    create_template = "custom/create.html"
    edit_template = "custom/edit.html"
    details_template = "custom/details.html"
    list_template = "custom/list.html"

    def scaffold_form(self):
        form_class = super(ResumeView, self).scaffold_form()
        form_class.extra = StringField('Extra')
        return form_class

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
    '''This view is same as the view above but allows file uploading'''

    form_extra_fields = {
        'path': form.ImageUploadField('Image',
                                      thumbnail_size=(1920, 1080, True))
    }

    # Custom filters
    can_view_details = True
    can_export = True
    can_set_page_size = True

    create_template = "custom/create.html"
    edit_template = "custom/edit.html"
    details_template = "custom/details.html"
    list_template = "custom/list.html"

    def scaffold_form(self):
        form_class = super(JobBoardView, self).scaffold_form()
        form_class.extra = StringField('Extra')
        return form_class

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

    def scaffold_form(self):
        form_class = super(InsightsView, self).scaffold_form()
        form_class.extra = StringField('Extra')
        return form_class

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
admin._set_admin_index_view(index_view=HomeAdminView())
admin.base_template = "admin/base.html"
admin.name = name = "PortfolioMe"
admin.add_view(ApplicantView(models.Applicant, db.session))
admin.add_view(ResumeView(models.Resume, db.session))
admin.add_view(JobBoardView(models.JobBoard, db.session))
admin.add_view(InsightsView(models.Insights, db.session))
admin.add_view(ManageAdminView(name="Manage Admin", endpoint="manage_admin"))
admin.add_view(LogoutAdminView(name="Logout", endpoint="logout"))
