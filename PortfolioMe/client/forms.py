from flask_wtf import FlaskForm
from wtforms import (StringField, TelField, RadioField,
                     SubmitField, BooleanField, URLField, IntegerField, MultipleFileField, TextAreaField)
from wtforms.validators import DataRequired, Length, Email, URL, Regexp, NumberRange, ValidationError
from flask_wtf.file import FileAllowed, FileRequired, FileField
from flask_login import current_user
from PortfolioMe.models import Applicant
from PortfolioMe.constants import marital_status_types, gender_radio


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    mailing_address = StringField(
        'Mailing Address', validators=[DataRequired()])
    phone_number = TelField('Phone Number', validators=[
        DataRequired(), Length(min=8, max=11, message="Follows Malaysian phone number format."), Regexp(r"(01)[0-9]{1}[0-9]{6,8}", message="Phone number is 9 to 11 characters without dash.")])
    gender = RadioField('Gender', validators=[
                        DataRequired()], choices=gender_radio)
    submit = SubmitField('Save Changes')

    def validate_username(self, username):
        if username.data != current_user.username:
            applicant = Applicant.query.filter_by(
                username=username.data).first()
            if applicant:
                raise ValidationError(
                    'This username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            applicant = Applicant.query.filter_by(email=email.data).first()
            if applicant:
                raise ValidationError(
                    'This email is taken. Please choose a different one.')


class ResumeSubmissionForm(FlaskForm):
    resume = FileField('Resume', validators=[
                       FileRequired(), FileAllowed(['pdf'])])
    documents = MultipleFileField('Additional Documents', validators=[
        FileAllowed(['pdf', 'jpg', 'png', 'jpeg'])])
    submit = SubmitField('Send resume')


class PersonalParticularsForm(FlaskForm):
    '''Basically resume_details form'''

    name = StringField('Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(18, 65)])
    ic = StringField('IC', validators=[DataRequired(), Regexp(
        r"[0-9]{6}[0-9]{2}[0-9]{4}", message="Follows Malaysian IC format")])
    dob = StringField('Date of Birth(DOB)', validators=[DataRequired()])
    mailing_address = StringField(
        'Mailing address', validators=[DataRequired()])
    postcode = StringField('Postcode', validators=[
                           DataRequired(), Regexp(r"[0-9]{5}")])
    town = StringField('Town', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    gender = RadioField('Gender', validators=[
                        DataRequired()], choices=gender_radio)
    phone_number = StringField('Phone Number', validators=[DataRequired(), Regexp(
        r"(01)[0-9]{1}[0-9]{6,8}", message="Phone number is 9 to 11 characters without dash.")])
    marital_status = RadioField('Marital Status', validators=[
        DataRequired()], choices=marital_status_types, default=marital_status_types[0])
    linkedin_url = URLField('LinkedIn URL', validators=[DataRequired(), URL()])
    skills = TextAreaField('Skills', validators=[DataRequired()])
    soft_skills = TextAreaField('Soft skills', validators=[DataRequired()])
    work_experience = TextAreaField(
        'Work Experience', validators=[DataRequired()])
    agreement = BooleanField(
        'I agree that the data submitted here is valid', validators=None)
    submit = SubmitField('Confirm')

    def validate_agreement(self, agreement):
        if agreement.data == False:
            raise ValidationError(
                'Please tick the checkbox above.')
