import os
from flask import Blueprint, current_app, jsonify, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy import not_
from PortfolioMe import db, constants
from PortfolioMe.client.forms import EditProfileForm, PersonalParticularsForm, ResumeSubmissionForm
from PortfolioMe.models import JobBoard, Resume, Resume_Details
from PortfolioMe.client.utils import save_resume, parse_resume

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
    '''
    *
    * not_(JobBoard.resumes_submitted_list.any(applicant_id=current_user.id))
    *
    - This query is to filter out the jobs the current applicant has submitted and 
        only display the jobs that the applicant has not submitted otherwise if they 
        submit their resumes to the same job twice there will a SQL error
    '''

    JOBS_PER_PAGE = 12
    page = request.args.get('page', default=1, type=int)
    if current_user.is_authenticated:
        jobs = JobBoard.query.filter(not_(JobBoard.resumes_submitted_list.any(
            applicant_id=current_user.id))).order_by(
            JobBoard.id.asc()).paginate(page=page, per_page=JOBS_PER_PAGE)
    else:
        jobs = JobBoard.query.order_by(
            JobBoard.id.asc()).paginate(page=page, per_page=JOBS_PER_PAGE)

    # Searching
    search_query = request.args.get('search')
    if search_query is not None:
        jobs = JobBoard.query.filter(JobBoard.name.like(f"%{search_query}%"), not_(JobBoard.resumes_submitted_list.any(
            applicant_id=current_user.id))).order_by(
            JobBoard.id.asc()).paginate(page=page, per_page=JOBS_PER_PAGE)

    # Filtering
    jobtype_filter = constants.job_types
    department_filter = constants.department_types
    type = request.args.get('type')
    min_salary = request.args.get('min_salary')
    max_salary = request.args.get('max_salary')
    department = request.args.get('dept')

    if type != "All" and min_salary and max_salary and department != "All":
        jobs = JobBoard.query.filter(JobBoard.job_type.like(f"%{type}%"), (JobBoard.min_salary > min_salary) | (JobBoard.max_salary < max_salary), JobBoard.department.like(f"%{department}%"), not_(JobBoard.resumes_submitted_list.any(
            applicant_id=current_user.id))).order_by(
            JobBoard.id.asc()).paginate(page=page, per_page=JOBS_PER_PAGE)
    elif type == "All" and min_salary and max_salary and department == "All":
        jobs = JobBoard.query.filter((JobBoard.min_salary > min_salary) | (JobBoard.max_salary < max_salary), not_(JobBoard.resumes_submitted_list.any(
            applicant_id=current_user.id))).order_by(
            JobBoard.id.asc()).paginate(page=page, per_page=JOBS_PER_PAGE)
    elif type == "All" and min_salary and max_salary and department:
        jobs = JobBoard.query.filter((JobBoard.min_salary > min_salary) | (JobBoard.max_salary < max_salary), JobBoard.department.like(f"%{department}%"), not_(JobBoard.resumes_submitted_list.any(
            applicant_id=current_user.id))).order_by(
            JobBoard.id.asc()).paginate(page=page, per_page=JOBS_PER_PAGE)
    elif type and min_salary and max_salary and department == "All":
        jobs = JobBoard.query.filter(JobBoard.job_type.like(f"%{type}%"), (JobBoard.min_salary > min_salary) | (JobBoard.max_salary < max_salary), not_(JobBoard.resumes_submitted_list.any(
            applicant_id=current_user.id))).order_by(
            JobBoard.id.asc()).paginate(page=page, per_page=JOBS_PER_PAGE)

    return render_template("client/job_board.html", jobs=jobs, jobtype_filter=jobtype_filter, department_filter=department_filter)


@client.route("/job_board/<int:job_id>", methods=["GET", "POST"])
def job_detail(job_id):
    job = JobBoard.query.get_or_404(job_id)
    form = ResumeSubmissionForm()

    if form.validate_on_submit():
        # parse resume
        resume_name = save_resume(form.resume.data)
        resume = Resume(applicant_details='parsed text', image=resume_name,
                        applicant_id=current_user.id, job_id=job.id)
        db.session.add(resume)
        db.session.commit()
        resume_details = Resume_Details(name='lol', age=34, ic='2049823', dob='12-02-1234',
                                        mailing_address='diajeodiaeoidj', postcode='14100',
                                        town='Somewhere', state='no where', gender='Male',
                                        phone_number=42034987, marital_status='none',
                                        linkedin_url='bla bla bla', education='nothing',
                                        certificates='degree in failure', skills='nothing',
                                        soft_skills='Not soft', work_experience='No experience at all',
                                        applicant_id=current_user.id, resume_id=resume.id)
        db.session.add(resume_details)
        db.session.commit()
        return redirect(url_for("client.upload_resume_details", job_id=job.id, resume_details_id=resume_details.id))

    return render_template("client/job_detail.html", job=job, form=form)


@client.route("/job_board/<int:job_id>/upload_resume_details/<int:resume_details_id>", methods=["GET", "POST"])
@login_required
def upload_resume_details(job_id, resume_details_id):
    job = JobBoard.query.get_or_404(job_id)
    resume_details = Resume_Details.query.get_or_404(resume_details_id)
    form = PersonalParticularsForm()

    if form.validate_on_submit():
        # save resume details
        flash("Your form has been saved.", "success")
        return redirect(url_for("client.job_board"))
    return render_template("client/upload_resume_details.html", form=form)


@client.route("/resume_status")
@login_required
def resume_status():
    resumes = Resume.query.filter_by(applicant_id=current_user.id).all()
    return render_template("client/resume_status.html", resumes=resumes)
