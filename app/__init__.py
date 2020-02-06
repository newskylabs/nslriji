
import os
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l

from config import Config

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

# Login message (overwriting the default to get localization)
login.login_message = _l('Please log in to access this page.')

# Flask-Mail instance
mail = Mail(app)

# Flask-Bootstrap
bootstrap = Bootstrap(app)

# Flask-Moment
# For adjusting the time informations to the local time
moment = Moment(app)

# Flask-Babel
# i18n and l10n support
babel = Babel(app)

# ==================
# Set up logging
# ------------------

def setup_file_log_handler():
    """Logging to log files"""

    if not os.path.exists('logs'):
        os.mkdir('logs')

    # Rotating log files:
    # - log file: logs/riji.log
    # - Max log file size: 10KB
    # - Max number of log files: 10
    file_handler = RotatingFileHandler('logs/riji.log', 
                                       maxBytes=10240,
                                       backupCount=10)

    # Log message formatter: 
    # timestamp, log level, message, source file, line number
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))

    # Log level for log files: INFO
    file_handler.setLevel(logging.INFO)

    app.logger.addHandler(file_handler)

def setup_email_log_handler():
    """Log ERRORs by email"""

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
            toaddrs     = app.config['ADMINS'], subject='Riji Failure',
            credentials = auth, 
            secure      = secure
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

# (only when not in debug mode)
if not app.debug:

    # Setup logging to log files
    setup_file_log_handler()

    # Setup logging via email
    setup_email_log_handler()

    # Set log level to INFO
    app.logger.setLevel(logging.INFO)

    # A first startup INFO log message
    app.logger.info('Riji startup')


@babel.localeselector
def get_locale():
    locale = request.accept_languages.best_match(app.config['LANGUAGES'])
    return locale


# Routes and models 
# have to be imported at the end to avoid circular imports
from app import routes, models, errors
    
## fin.
