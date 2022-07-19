from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SubmitField, SearchField
from wtforms.validators import DataRequired


class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class AdminEditResumeForm(FlaskForm):
    is_bookmarked = BooleanField('Bookmark', validators=None)
    is_hired = BooleanField('Hire', validators=None)
    applicant_details = TextAreaField(
        'Applicant Details', validators=None)
    submit = SubmitField('Save Changes')


class AdminSearchForm(FlaskForm):
    search = SearchField('', validators=None, id='searchBar')
    submit = SubmitField('Search', id='search')
