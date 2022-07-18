import os
from flask import Blueprint, jsonify, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from PortfolioMe import db
from PortfolioMe.client.forms import EditProfileForm, ResumeSubmissionForm
from PortfolioMe.models import JobBoard, Resume
from PortfolioMe.client.utils import save_resume, parse_resume, convert_pdf

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
        return redirect(url_for("client.edit_profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone_number.data = current_user.phone_number
        form.gender.data = current_user.gender
        form.organization.data = current_user.organization
    return render_template("client/edit_profile.html", form=form)


@client.route("/job_board")
def job_board():
    jobs = JobBoard.query.all()
    return render_template("client/job_board.html", jobs=jobs)


@client.route("/job_board/<int:job_id>")
def job_detail(job_id):
    job = JobBoard.query.get_or_404(job_id)
    return render_template("client/job_detail.html", job=job)


@client.route("/job_board/<int:job_id>/upload_resume", methods=["GET", "POST"])
@login_required
def upload_resume(job_id):
    job = JobBoard.query.get_or_404(job_id)
    form = ResumeSubmissionForm()
    if form.validate_on_submit():
        resume_name = save_resume(form.resume.data)
        resume = Resume(applicant_details=form.output.data, image=resume_name,
                        applicant_id=current_user.id, job_id=job.id)
        db.session.add(resume)
        db.session.commit()
        flash("Your resume has been saved.", "success")
        return redirect(url_for("client.job_board"))
    return render_template("client/upload_resume.html", form=form)


# API endpoint for AJAX request
@client.route("/parse_image", methods=["GET", "POST"])
def parse_image():
    if request.method == "POST":
        _, file_extension = os.path.splitext(request.files["file"].filename)
        if file_extension == ".pdf":
            file = request.files["file"].read()
            resume = convert_pdf(file)
            parsed_text = parse_resume(resume, False)
        else:
            resume = request.files["file"].read()
            parsed_text = parse_resume(resume, True)
        return jsonify({"status": "success", "parsed_text": parsed_text})


@client.route("/resume_list")
@login_required
def resume_list():
    resumes = Resume.query.filter_by(applicant_id=current_user.id).all()
    return render_template("client/resume_list.html", resumes=resumes)
