from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, message="Minimum length is %(min)d characters.")])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password')])
    phone_number = StringField('Phone Number', validators=[
        DataRequired(), Length(min=8, max=11, message="Follows Malaysian phone number format."), Regexp(r"(01)[0-9]{1}[0-9]{6,8}", message="Phone number is 9 to 11 characters without dash.")])
    # Radio field
    radio = ["Male", "Female", "Prefer not to say"]
    gender = RadioField('Gender', validators=[DataRequired()], choices=radio)
    #
    organization = StringField('Organization', validators=[DataRequired()])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[
                        DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, message="Minimum length is %(min)d characters.")])
    phone_number = StringField('Phone Number', validators=[
                        DataRequired(), Length(min=8, max=11, message="Follows Malaysian phone number format."), Regexp(r"(01)[0-9]{1}[0-9]{6,8}", message="Phone number is 9 to 11 characters without dash.")])
    # Radio field
    radio = ["Male", "Female", "Prefer not to say"]
    gender = RadioField('Gender', validators=[DataRequired()], choices=radio)
    #
    organization = StringField('Organization', validators=[DataRequired()])
    submit = SubmitField('Save Changes')

class ResumeSubmissionForm(FlaskForm):
    resume = FileField('Resume', validators=[DataRequired()])
    submit = SubmitField('Send resume')