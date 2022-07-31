from flask import render_template
from PortfolioMe import mail
from flask_mail import Message


def send_reset_email(applicant):
    # Function to send email to user for resetting password
    token = applicant.get_reset_token()
    msg = Message("Password Reset Request",
                  sender="noreply@PortfolioMe.com", recipients=[applicant.email])
    msg.html = render_template(
        "custom/email_body.html", token=token, username=applicant.username)
    mail.send(msg)


def send_admin_email(applicant, subject, message):
    msg = Message(subject=subject,
                  sender=applicant.email, recipients=["PortfolioMe.service@gmail.com"])
    msg.html = f"{message} My email is {applicant.email}"
    mail.send(msg)
