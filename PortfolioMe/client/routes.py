from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from PortfolioMe import db
from PortfolioMe.client.forms import EditProfileForm, ResumeSubmissionForm
from PortfolioMe.models import JobBoard

client = Blueprint("client", __name__)


@client.route("/edit_profile", methods=["GET", "POST"])
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


@client.route("/job_board")
@login_required
def job_board():
    jobs = JobBoard.query.all()
    return render_template("client/job_board.html", jobs=jobs)


@client.route("/job_board/<int:job_id>")
@login_required
def job_detail(job_id):
    job = JobBoard.query.get_or_404(job_id)
    return render_template("client/job_detail.html", job=job)


@client.route("/job_board/<int:job_id>/upload_resume")
@login_required
def upload_resume(job_id):
    job = JobBoard.query.get_or_404(job_id)
    form = ResumeSubmissionForm()
    return render_template("client/upload_resume.html", form=form)


@client.route("/resume_list")
@login_required
def resume_list():
    return render_template("client/resume_list.html")
