from flask import url_for
from PortfolioMe import mail
from flask_mail import Message


def send_reset_email(applicant):
    # Function to send email to user for resetting password
    token = applicant.get_reset_token()
    msg = Message("Password Reset Request",
                  sender="noreply@PortfolioMe.com", recipients=[applicant.email])
    msg.body = f'''To reset your password, visit the following link: 
{url_for("reset_token", token=token, _external=True)}
    
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)
