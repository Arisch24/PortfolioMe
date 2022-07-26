import os
from flask import Blueprint, jsonify, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from PortfolioMe import db, constants
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
        current_user.mailing_address = form.mailing_address.data
        current_user.phone_number = form.phone_number.data
        current_user.gender = form.gender.data
        db.session.commit()
        flash(f"Profile updated successfully.", "success")
        return redirect(url_for("client.edit_profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.mailing_address.data = current_user.mailing_address
        form.phone_number.data = current_user.phone_number
        form.gender.data = current_user.gender
    return render_template("client/edit_profile.html", form=form)


@client.route("/job_board", methods=["GET", "POST"])
def job_board():
    JOBS_PER_PAGE = 12
    page = request.args.get('page', default=1, type=int)
    jobs = JobBoard.query.order_by(
        JobBoard.id.asc()).paginate(page=page, per_page=JOBS_PER_PAGE)

    # Searching
    search_query = request.args.get('search')
    if search_query is not None:
        jobs = JobBoard.query.filter(JobBoard.name.like(f"%{search_query}%")).order_by(
            JobBoard.id.asc()).paginate(page=page, per_page=JOBS_PER_PAGE)

    # Filtering
    jobtype_filter = constants.job_types
    department_filter = constants.department_types
    type = request.args.get('type')
    min_salary = request.args.get('min_salary')
    max_salary = request.args.get('max_salary')
    department = request.args.get('dept')

    if type != "All" and min_salary and max_salary and department != "All":
        jobs = JobBoard.query.filter(JobBoard.job_type.like(f"%{type}%"), (JobBoard.min_salary > min_salary) | (JobBoard.max_salary < max_salary), JobBoard.department.like(f"%{department}%")).order_by(
            JobBoard.id.asc()).paginate(page=page, per_page=JOBS_PER_PAGE)
    elif type == "All" and min_salary and max_salary and department == "All":
        jobs = JobBoard.query.filter((JobBoard.min_salary > min_salary) | (JobBoard.max_salary < max_salary)).order_by(
            JobBoard.id.asc()).paginate(page=page, per_page=JOBS_PER_PAGE)
    elif type == "All" and min_salary and max_salary and department:
        jobs = JobBoard.query.filter((JobBoard.min_salary > min_salary) | (JobBoard.max_salary < max_salary), JobBoard.department.like(f"%{department}%")).order_by(
            JobBoard.id.asc()).paginate(page=page, per_page=JOBS_PER_PAGE)
    elif type and min_salary and max_salary and department == "All":
        jobs = JobBoard.query.filter(JobBoard.job_type.like(f"%{type}%"), (JobBoard.min_salary > min_salary) | (JobBoard.max_salary < max_salary)).order_by(
            JobBoard.id.asc()).paginate(page=page, per_page=JOBS_PER_PAGE)

    return render_template("client/job_board.html", jobs=jobs, jobtype_filter=jobtype_filter, department_filter=department_filter)


@client.route("/job_board/<int:job_id>")
def job_detail(job_id):
    job = JobBoard.query.get_or_404(job_id)
    form = ResumeSubmissionForm()
    return render_template("client/job_detail.html", job=job, form=form)


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
