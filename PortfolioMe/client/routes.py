import os
import random
from cv2 import reduce
from werkzeug.datastructures import FileStorage
from flask import Blueprint, current_app, jsonify, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy import not_
from PortfolioMe import db, constants
from PortfolioMe.client.forms import EditProfileForm, PersonalParticularsForm, ResumeSubmissionForm
from PortfolioMe.models import JobBoard, Resume, Resume_Details
from PortfolioMe.client.utils import convert_pdf, extract_resume_data, save_multiple_documents, save_resume, parse_resume

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

    JOBS_PER_PAGE = 9
    page = request.args.get('page', default=1, type=int)
    if current_user.is_authenticated:
        jobs = JobBoard.query.filter(not_(JobBoard.resumes_submitted_list.any(
            applicant_id=current_user.id))).order_by(
            JobBoard.name.asc()).paginate(page=page, per_page=JOBS_PER_PAGE)
    else:
        jobs = JobBoard.query.order_by(
            JobBoard.name.asc()).paginate(page=page, per_page=JOBS_PER_PAGE)

    # Searching
    search_query = request.args.get('search')
    if search_query is not None and current_user.is_authenticated:
        jobs = JobBoard.query.filter(JobBoard.name.like(f"%{search_query}%"), not_(JobBoard.resumes_submitted_list.any(
            applicant_id=current_user.id))).order_by(
            JobBoard.name.asc()).paginate(page=page, per_page=JOBS_PER_PAGE)
    elif search_query is not None and not current_user.is_authenticated:
        jobs = JobBoard.query.filter(JobBoard.name.like(f"%{search_query}%")).order_by(
            JobBoard.name.asc()).paginate(page=page, per_page=JOBS_PER_PAGE)

    # Filtering
    jobtype_filter = constants.job_types
    department_filter = constants.department_types
    type = request.args.get('type', 'All')
    min_salary = request.args.get('min_salary', 0)
    max_salary = request.args.get('max_salary', 20000)
    department = request.args.get('dept', 'All')

    if current_user.is_authenticated:
        if type != "All" and min_salary and max_salary and department != "All":
            print("1st")
            jobs = JobBoard.query.filter(JobBoard.job_type.like(f"%{type}%"), (JobBoard.min_salary > min_salary), (JobBoard.max_salary < max_salary), JobBoard.department.like(f"%{department}%"), not_(JobBoard.resumes_submitted_list.any(
                applicant_id=current_user.id))).order_by(
                JobBoard.name.asc()).paginate(page=page, per_page=JOBS_PER_PAGE)
        elif type == "All" and min_salary and max_salary and department == "All":
            print("2nd")
            jobs = JobBoard.query.filter((JobBoard.min_salary > min_salary), (JobBoard.max_salary < max_salary), not_(JobBoard.resumes_submitted_list.any(
                applicant_id=current_user.id))).order_by(
                JobBoard.name.asc()).paginate(page=page, per_page=JOBS_PER_PAGE)
        elif type == "All" and min_salary and max_salary and department:
            print("3rd")
            jobs = JobBoard.query.filter((JobBoard.min_salary > min_salary), (JobBoard.max_salary < max_salary), JobBoard.department.like(f"%{department}%"), not_(JobBoard.resumes_submitted_list.any(
                applicant_id=current_user.id))).order_by(
                JobBoard.name.asc()).paginate(page=page, per_page=JOBS_PER_PAGE)
        elif type and min_salary and max_salary and department == "All":
            print("4th")
            jobs = JobBoard.query.filter(JobBoard.job_type.like(f"%{type}%"), (JobBoard.min_salary > min_salary),  (JobBoard.max_salary < max_salary), not_(JobBoard.resumes_submitted_list.any(
                applicant_id=current_user.id))).order_by(
                JobBoard.name.asc()).paginate(page=page, per_page=JOBS_PER_PAGE)
    else:
        if type != "All" and min_salary and max_salary and department != "All":
            jobs = JobBoard.query.filter(JobBoard.job_type.like(f"%{type}%"), (JobBoard.min_salary > min_salary), (JobBoard.max_salary < max_salary), JobBoard.department.like(f"%{department}%")).order_by(
                JobBoard.name.asc()).paginate(page=page, per_page=JOBS_PER_PAGE)
        elif type == "All" and min_salary and max_salary and department == "All":
            jobs = JobBoard.query.filter((JobBoard.min_salary > min_salary), (JobBoard.max_salary < max_salary)).order_by(
                JobBoard.name.asc()).paginate(page=page, per_page=JOBS_PER_PAGE)
        elif type == "All" and min_salary and max_salary and department:
            jobs = JobBoard.query.filter((JobBoard.min_salary > min_salary), (JobBoard.max_salary < max_salary), JobBoard.department.like(f"%{department}%")).order_by(
                JobBoard.name.asc()).paginate(page=page, per_page=JOBS_PER_PAGE)
        elif type and min_salary and max_salary and department == "All":
            jobs = JobBoard.query.filter(JobBoard.job_type.like(f"%{type}%"), (JobBoard.min_salary > min_salary), (JobBoard.max_salary < max_salary)).order_by(
                JobBoard.name.asc()).paginate(page=page, per_page=JOBS_PER_PAGE)

    return render_template("client/job_board.html", jobs=jobs, jobtype_filter=jobtype_filter, department_filter=department_filter)


@client.route("/job_board/<int:job_id>", methods=["GET", "POST"])
def job_detail(job_id):
    job = JobBoard.query.get_or_404(job_id)
    form = ResumeSubmissionForm()

    def get_dob_from_ic(ic):
        ic = ic[0:6]
        year = ic[0:2]
        month = ic[2:4]
        day = ic[4:6]
        if int(year) < 22:
            year = "20" + year
        elif int(year) > 22:
            year = "19" + year
        dob = f"{day}-{month}-{year}"
        return dob

    if form.validate_on_submit():

        # save resume
        resume_name = save_resume(form.resume.data)
        resume_path = os.path.join(
            current_app.root_path, 'static/resumes', resume_name)

        file = None
        parsed_text = None
        with open(resume_path, 'rb') as fp:
            file = FileStorage(fp)
            # parse resume
            image = convert_pdf(file.read())
            parsed_text = parse_resume(image)

        # clean raw text data
        json_dict = extract_resume_data(parsed_text)

        if form.documents.data:
            documents_list = save_multiple_documents(form.documents.data)
        documents_list = ", ".join(documents_list)
        resume = Resume(applicant_details=parsed_text, image=resume_name,
                        additional_documents=documents_list,
                        applicant_id=current_user.id, job_id=job.id)
        db.session.add(resume)
        db.session.commit()

        # save resume_details
        resume_details = Resume_Details(name=json_dict.get("name", current_user.username),
                                        age=json_dict.get(
                                            "age", random.randint(18, 40)),
                                        ic=json_dict.get(
                                            "ic", current_user.ic),
                                        dob=json_dict.get(
                                            "dob", get_dob_from_ic(current_user.ic)),
                                        mailing_address=json_dict.get(
                                            "address", current_user.mailing_address),
                                        postcode=json_dict.get(
                                            "postcode", 'Not found'),
                                        town=json_dict.get(
                                            "town", 'Not found'),
                                        state=json_dict.get(
                                            "state", 'Not found'),
                                        gender=current_user.gender,
                                        phone_number=json_dict.get(
                                            "phone_number", 'Not found'),
                                        marital_status=json_dict.get(
                                            "marital_status", 'Not found'),
                                        linkedin_url=json_dict.get(
                                            "linked_in_url", 'Not found'),
                                        education=json_dict.get(
                                            "education", 'Not found'),
                                        certificates=json_dict.get(
                                            "certificates", 'Not found'),
                                        skills=json_dict.get(
                                            "skills", 'Not found'),
                                        soft_skills=json_dict.get(
                                            "soft_skills", 'Not found'),
                                        work_experience=json_dict.get(
                                            "work_experience", 'Not found'),
                                        applicant_id=current_user.id,
                                        resume_id=resume.id)
        db.session.add(resume_details)
        db.session.commit()
        return redirect(url_for("client.upload_resume_details", job_id=job.id, resume_details_id=resume_details.id))

    return render_template("client/job_detail.html", job=job, form=form)


@client.route("/job_board/<int:job_id>/upload_resume_details/<int:resume_details_id>", methods=["GET", "POST"])
@login_required
def upload_resume_details(job_id, resume_details_id):
    job = JobBoard.query.get_or_404(job_id)
    resume_details = Resume_Details.query.get_or_404(resume_details_id)
    resume = Resume.query.filter_by(id=resume_details.resume_id).first()

    if resume.status != "Pending":
        flash("Your resume is not allowed to be edited anymore", "failed")
        return redirect(url_for("client.resume_status"))

    form = PersonalParticularsForm()

    if form.validate_on_submit():
        # save resume details
        resume_details.name = form.name.data
        resume_details.age = form.age.data
        resume_details.ic = form.ic.data
        resume_details.dob = form.dob.data
        resume_details.mailing_address = form.mailing_address.data
        resume_details.postcode = form.postcode.data
        resume_details.town = form.town.data
        resume_details.state = form.state.data
        resume_details.gender = form.gender.data
        resume_details.phone_number = form.phone_number.data
        resume_details.marital_status = form.marital_status.data
        resume_details.linkedin_url = form.linkedin_url.data
        resume_details.education = form.education.data
        resume_details.certificates = form.certificates.data
        resume_details.skills = form.skills.data
        resume_details.soft_skills = form.soft_skills.data
        resume_details.work_experience = form.work_experience.data
        db.session.commit()
        flash("Your form has been saved.", "success")
        return redirect(url_for("client.job_board"))
    elif request.method == "GET":
        form.name.data = resume_details.name
        form.age.data = resume_details.age
        form.ic.data = resume_details.ic
        form.dob.data = resume_details.dob
        form.mailing_address.data = resume_details.mailing_address
        form.postcode.data = resume_details.postcode
        form.town.data = resume_details.town
        form.state.data = resume_details.state
        form.gender.data = resume_details.gender
        form.phone_number.data = resume_details.phone_number
        form.marital_status.data = resume_details.marital_status
        form.linkedin_url.data = resume_details.linkedin_url
        form.education.data = resume_details.education
        form.certificates.data = resume_details.certificates
        form.skills.data = resume_details.skills
        form.soft_skills.data = resume_details.soft_skills
        form.work_experience.data = resume_details.work_experience
    return render_template("client/upload_resume_details.html", form=form)


@client.route("/resume_status")
@login_required
def resume_status():
    resumes = Resume.query.filter_by(applicant_id=current_user.id).all()
    jobs = JobBoard.query.filter(JobBoard.resumes_submitted_list.any(
        applicant_id=current_user.id)).all()
    return render_template("client/resume_status.html", resumes=resumes, jobs=jobs)
