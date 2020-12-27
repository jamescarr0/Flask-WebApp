from flask import render_template, current_app
from app.email import send_email


def send_password_reset_email(user):
    """ 
        Sends an email to a registered user to reset account password. 
        A token is generated and validated before user is able to change password.
    """

    token = user.get_password_reset_token()

    send_email(
        current_app.config['MAIL_RESET_PASSWORD_SUBJECT'],
        sender=current_app.config['ADMINS'][0],
        recipients=[user.email],
        text_body=render_template(
            'email/reset_password.txt',
            signature=current_app.config['MAIL_RESET_PASSWORD_SIGNATURE'],
            user=user,
            token=token),
        html_body=render_template(
            'email/reset_password.html',
            signature=current_app.config['MAIL_RESET_PASSWORD_SIGNATURE'],
            user=user,
            token=token)
    )
