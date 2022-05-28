from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password')])
    phone_number = StringField('Phone Number', validators=[
        DataRequired(), Length(min=8, max=11)])
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
    password = PasswordField('Password', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[
                        DataRequired(), Length(min=8, max=11)])
    # Radio field
    radio = ['Male', 'Female']
    gender = RadioField('Gender', validators=[DataRequired()], choices=radio)
    #
    organization = StringField('Organization', validators=[DataRequired()])
    submit = SubmitField('Save Changes')
