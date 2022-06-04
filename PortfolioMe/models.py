from datetime import datetime
from PortfolioMe import db


class Applicant(db.Model):
    __tablename__ = 'applicant'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=False, nullable=False)
    password = db.Column(db.String(60), unique=False, nullable=False)
    gender = db.Column(db.String(10), unique=False, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    phone_number = db.Column(db.Integer, unique=False, nullable=False)
    organization = db.Column(db.String(50), unique=False, nullable=False)
    resumes_owned = db.relationship('Resume', backref='associated_applicant')

    def __repr__(self):
        return f"Applicant('{self.username}', '{self.password}', '{self.gender}', '{self.email}', '{self.phone_number}', {self.organization}', '{self.resumes_owned}'"


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=False, nullable=False)
    password = db.Column(db.String(60), unique=False, nullable=False)
    gender = db.Column(db.String(10), unique=False, nullable=False)

    def __repr__(self):
        return f"Admin('{self.username}', '{self.password}', '{self.gender}'"


class Resume(db.Model):
    __tablename__ = 'resume'

    id = db.Column(db.Integer, primary_key=True)
    applicant_details = db.Column(db.Text, unique=False, nullable=False)
    date_edited = db.Column(db.DateTime, unique=False, nullable=False,
                            default=datetime.utcnow)
    is_bookmarked = db.Column(db.Boolean, unique=False, nullable=False, default=False)
    is_hired = db.Column(db.Boolean, unique=False, nullable=False, default=False)
    image = db.Column(db.String(50), unique=False, nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey(
        'applicant.id'), unique=False, nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey(
        'jobboard.id'), unique=False, nullable=False)

    def __repr__(self):
        return f"Resume('{self.applicant_details}', '{self.date_edited}', '{self.is_bookmarked}', '{self.is_hired}', '{self.applicant_id}', '{self.job_id}')"


class JobBoard(db.Model):
    __tablename__ = 'jobboard'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    salary = db.Column(db.Float, nullable=False)
    job_type = db.Column(db.String(10), nullable=False)
    job_image = db.Column(db.String(50), nullable=False)
    resumes_submitted_list = db.relationship(
        'Resume', backref='associated_job_board', lazy=True)

    def __repr__(self):
        return f"JobBoard('{self.name}', '{self.description}', '{self.department}', '{self.salary}', '{self.job_type}', '{self.resumes_submitted_list}'"


class Insights(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resume_count = db.Column(db.Integer, unique=False, nullable=False)
    bookmark_count = db.Column(db.Integer, unique=False, nullable=False)
    hired_count = db.Column(db.Integer, unique=False, nullable=False)

    def __repr__(self):
        return f"Insights('{self.resume_count}', '{self.bookmark_count}', '{self.hired_count}'"