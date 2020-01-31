## =========================================================
## app/email.py
## ---------------------------------------------------------

from threading import Thread
from flask import render_template
from flask_mail import Message
from app import app, mail

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
    Thread(target=send_async_email, args=(app, msg)).start()

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Microblog] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))

## =========================================================
## =========================================================

## fin.
