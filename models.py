from datetime import datetime
from email.policy import default
from flask_sqlalchemy import SQLAlchemy
from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)


class Applicant(db.Model):
    __tablename__ = 'applicant'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=False, nullable=False)
    password = db.Column(db.String(60), unique=False, nullable=False)
    gender = db.Column(db.String(10), unique=False, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    phone_number = db.Column(db.Integer, unique=False, nullable=False)
    organization = db.Column(db.String(50), unique=False, nullable=False)
    resumes_owned = db.relationship('Resume', backref='resume')

    def __repr__(self):
        return f"Applicant('{self.username}', '{self.gender}', '{self.email}', '{self.phone_number}', {self.organization}'"


class Resume(db.Model):
    __tablename__ = 'resume'

    id = db.Column(db.Integer, primary_key=True)
    applicant_details = db.Column(db.Text, nullable=False)
    date_edited = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)
    is_bookmarked = db.Column(db.Boolean, nullable=False, default=False)
    is_hired = db.Column(db.Boolean, nullable=False, default=False)
    image = db.Column(db.String(50), nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey(
        'applicant.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey(
        'jobboard.id'), nullable=False)

    def __repr__(self):
        return f"Resume('{self.applicant_details}', '{self.date_edited}', '{self.applicant_id}', '{self.job_id}')"


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
        'Resume', backref='resume', lazy=True)

    def __repr__(self):
        return f"JobBoard('{self.name}', '{self.description}', '{self.department}', '{self.salary}', {self.resumes}'"
