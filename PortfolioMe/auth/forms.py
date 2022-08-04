from tokenize import String
from flask_wtf import FlaskForm
from pyparsing import Regex
from wtforms import StringField, PasswordField, TelField, RadioField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, ValidationError
from PortfolioMe.models import Applicant
from PortfolioMe.constants import gender_radio


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    ic = StringField('IC/My Kad', validators=[DataRequired(), Regexp(
        r"[0-9]{6}-[0-9]{2}-[0-9]{4}", message="Follows Malaysian IC format e.g XXXXXX-XX-XXXX")])
    mailing_address = StringField(
        'Mailing Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(
        min=8, message="Minimum length is %(min)d characters.")])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password')])
    phone_number = TelField('Phone Number', validators=[
        DataRequired(), Length(min=8, max=11, message="Follows Malaysian phone number format."), Regexp(r"(01)[0-9]{1}[0-9]{6,8}", message="Phone number is 9 to 11 characters without dash.")])
    gender = RadioField('Gender', validators=[
                        DataRequired()], choices=gender_radio)
    submit = SubmitField('Register')

    def validate_username(self, username):
        applicant = Applicant.query.filter_by(username=username.data).first()
        if applicant:
            raise ValidationError(
                'This username is taken. Please choose a different one.')

    def validate_email(self, email):
        applicant = Applicant.query.filter_by(email=email.data).first()
        if applicant:
            raise ValidationError(
                'This email is taken. Please choose a different one.')

    def validate_ic(self, ic):
        applicant = Applicant.query.filter_by(ic=ic.data).first()
        if applicant:
            raise ValidationError(
                'This ic is already registered. Either login or use a different ic.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        applicant = Applicant.query.filter_by(email=email.data).first()
        if not applicant:
            raise ValidationError(
                'There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(
        min=8, message="Minimum length is %(min)d characters.")])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
