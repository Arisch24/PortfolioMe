from datetime import datetime
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from PortfolioMe import db, login_manager
from flask_login import UserMixin, logout_user


@login_manager.user_loader
def load_user(user_id):
    applicant = Applicant.query.get(int(user_id))
    if applicant.status != "Active":
        return None and logout_user
    return applicant


class Applicant(db.Model, UserMixin):
    __tablename__ = 'applicant'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    ic = db.Column(db.String(12), unique=True, nullable=False)
    mailing_address = db.Column(db.String(100), unique=False, nullable=False)
    password = db.Column(db.String(60), unique=False, nullable=False)
    gender = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=False, nullable=False)
    resumes_owned = db.relationship(
        'Resume', backref='associated_applicant', uselist=True)
    status = db.Column(db.String(20), unique=False,
                       nullable=False, default='Active')
    last_active = db.Column(db.DateTime, unique=False, nullable=False,
                            default=datetime.utcnow)

    def get_reset_token(self):
        s = Serializer(current_app.config["SECRET_KEY"])
        return s.dumps({"applicant_id": self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            applicant_id = s.loads(token, expires_sec)['applicant_id']
        except:
            return None
        return Applicant.query.get(applicant_id)

    def __repr__(self):
        return f"Applicant('{self.username}', '{self.gender}', '{self.email}', '{self.phone_number}')"


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=False, nullable=False)
    password = db.Column(db.String(60), unique=False, nullable=False)
    gender = db.Column(db.String(10), unique=False, nullable=False)

    def __repr__(self):
        return f"Admin('{self.username}', '{self.gender}')"


class Resume(db.Model):
    __tablename__ = 'resume'

    id = db.Column(db.Integer, primary_key=True)
    applicant_details = db.Column(db.Text, unique=False, nullable=False)
    date_edited = db.Column(db.DateTime, unique=False, nullable=False,
                            default=datetime.utcnow)
    is_bookmarked = db.Column(db.Boolean, unique=False,
                              nullable=False, default=False)
    is_hired = db.Column(db.Boolean, unique=False,
                         nullable=False, default=False)
    status = db.Column(db.String(20), unique=False,
                       nullable=False, default="Pending")
    image = db.Column(db.String(50), unique=False, nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey(
        'applicant.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey(
        'jobboard.id'), nullable=False)
    resume_details_ref = db.relationship(
        'Resume_Details', backref='associated_resume', uselist=False)

    def __repr__(self):
        return f"Resume('{self.applicant_details}', '{self.date_edited}', '{self.is_bookmarked}', '{self.is_hired}', '{self.applicant_id}', '{self.job_id}')"


class Resume_Details(db.Model):
    __tablename__ = 'resumedetails'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False)
    age = db.Column(db.Integer, unique=False, nullable=False)
    ic = db.Column(db.String(12), unique=False, nullable=False)
    dob = db.Column(db.String(10), unique=False, nullable=False)
    mailing_address = db.Column(db.String(100), unique=False, nullable=False)
    postcode = db.Column(db.String(10), unique=False, nullable=False)
    town = db.Column(db.String(30), unique=False, nullable=False)
    state = db.Column(db.String(20), unique=False, nullable=False)
    gender = db.Column(db.String(20), unique=False, nullable=False)
    phone_number = db.Column(db.String(20), unique=False, nullable=False)
    marital_status = db.Column(db.String(20), unique=False, nullable=False)
    linkedin_url = db.Column(db.Text, unique=False, nullable=False)
    education = db.Column(db.Text, unique=False, nullable=False)
    certificates = db.Column(db.Text, unique=False, nullable=False)
    skills = db.Column(db.Text, unique=False, nullable=False)
    soft_skills = db.Column(db.Text, unique=False, nullable=False)
    work_experience = db.Column(db.Text, unique=False, nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey(
        'applicant.id'), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey(
        'resume.id'), nullable=False)

    def __repr__(self):
        return f"Resume_Details('{self.name}', '{self.age}', '{self.ic}', '{self.gender}', '{self.phone_number}', '{self.marital_status}', '{self.applicant_id}')"


class JobBoard(db.Model):
    __tablename__ = 'jobboard'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    highlights = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    department = db.Column(db.String(50), nullable=False)
    min_salary = db.Column(db.Float, nullable=False)
    max_salary = db.Column(db.Float, nullable=False)
    position_level = db.Column(db.String(20), nullable=False)
    years_of_experience = db.Column(db.String(10), nullable=False)
    job_type = db.Column(db.String(10), nullable=False)
    specializations = db.Column(db.String(50), nullable=False)
    job_image = db.Column(db.String(50), nullable=False)
    resumes_submitted_list = db.relationship(
        'Resume', backref='associated_job_board', lazy=True)

    def __repr__(self):
        return f"JobBoard('{self.name}', '{self.min_salary}', '{self.max_salary}', '{self.department}', '{self.job_type}', '{self.years_of_experience}', '{self.job_image}')"


class Insights(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resume_count = db.Column(db.Integer, unique=False, nullable=False)
    bookmark_count = db.Column(db.Integer, unique=False, nullable=False)
    hired_count = db.Column(db.Integer, unique=False, nullable=False)

    def __repr__(self):
        return f"Insights('{self.resume_count}', '{self.bookmark_count}', '{self.hired_count}')"
