## =========================================================
## app/email.py
## ---------------------------------------------------------

from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail


def send_async_email(app, msg):
    """
    Restore Flask's application context 
    and send email via flask_mail's Mail instance.
    """
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    """
    Send email asynchronously.
    """
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    # Send email asynchronously from a background thread.
    # flask_mail's Mail instance relies on Flask's application context
    # to send email.  Using send_async_email() to restore the context
    # and send the email.
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()


## =========================================================
## =========================================================

## fin.
