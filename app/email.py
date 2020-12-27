from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail


def async_send_email(app, msg):
    """ 
        Async function.
        Send emails as an asynchronous task.
    """
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    """ 
        Sends an email to the recipient 
    """

    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body

    # Send email as an async task.  Once complete the thread will end and
    # clean itself up.
    Thread(target=async_send_email, args=(current_app._get_current_object(), msg)).start()
