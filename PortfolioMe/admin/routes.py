from flask import Blueprint, session, redirect, url_for, request, flash, abort
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, Admin, expose, BaseView
from flask_login import current_user
from PortfolioMe import models, bcrypt, app, db
from PortfolioMe.admin.forms import AdminLoginForm
from PortfolioMe.models import Applicant, Resume, JobBoard, Insights

admin = Blueprint("admin", __name__)


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
