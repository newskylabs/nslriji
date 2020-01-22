
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging.handlers import SMTPHandler

# Application
app = Flask(__name__)

# Use the application config
app.config.from_object(Config)

# Database
db = SQLAlchemy(app)

# Database migration engine
migrate = Migrate(app, db)

# Login Manager
login = LoginManager(app)

# Login route
# Needed to automatically redirect users which have not logged in yet
# to the login page for pages which can only be seen after logging in.
login.login_view = 'login'

# Routes and models 
# have to be imported at the end to avoid circular imports
from app import routes, models, errors

# Log errors by email
if not app.debug:
    # Enable the email logger only when not in debug mode

    if app.config['MAIL_SERVER']:
        # Only when the mail server is specified in the environment

        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])

        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()

        mail_handler = SMTPHandler(
            mailhost    = (app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr    = 'no-reply@' + app.config['MAIL_SERVER'],
            toaddrs     = app.config['ADMINS'], subject='Microblog Failure',
            credentials = auth, 
            secure      = secure
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

## fin.
