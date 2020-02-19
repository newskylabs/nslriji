
import os
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l

from config import Config

## =========================================================
## Utilities
## ---------------------------------------------------------

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

    return file_handler

    
def setup_email_log_handler(config):
    """Log ERRORs by email"""

    auth = None
    if config['MAIL_USERNAME'] or config['MAIL_PASSWORD']:
        auth = (config['MAIL_USERNAME'], config['MAIL_PASSWORD'])

    secure = None
    if config['MAIL_USE_TLS']:
        secure = ()

    mail_handler = SMTPHandler(
        mailhost    = (config['MAIL_SERVER'], config['MAIL_PORT']),
        fromaddr    = 'no-reply@' + config['MAIL_SERVER'],
        toaddrs     = config['ADMINS'], subject='Riji Failure',
        credentials = auth, 
        secure      = secure
    )
    mail_handler.setLevel(logging.ERROR)

    return mail_handler


## =========================================================
## Components
## ---------------------------------------------------------

# Database
db = SQLAlchemy()

# Database migration engine
migrate = Migrate()

# Login Manager
login = LoginManager()

# Login route
# Needed to automatically redirect users which have not logged in yet
# to the login page for pages which can only be seen after logging in.
login.login_view = 'auth.login'

# Login message (overwriting the default to get localization)
login.login_message = _l('Please log in to access this page.')

# Flask-Mail instance
mail = Mail()

# Flask-Bootstrap
bootstrap = Bootstrap()

# Flask-Moment
# For adjusting the time informations to the local time
moment = Moment()

# Flask-Babel
# i18n and l10n support
babel = Babel()


def create_app(config_class=Config):

    # Application
    app = Flask(__name__)

    # Application config
    app.config.from_object(config_class)
    
    # Init components
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)

    # Register blueprints
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # Setup log handlers
    # when neither in debug nor test mode
    if not app.debug and not app.testing:

        # Setup logging to log files
        file_handler = setup_file_log_handler()
        app.logger.addHandler(file_handler)

        # Setup logging via email
        # when the mail server is specified in the environment
        if app.config['MAIL_SERVER']:
            mail_handler = setup_email_log_handler(app.config)
            app.logger.addHandler(mail_handler)

        # Set log level to INFO
        app.logger.setLevel(logging.INFO)

        # A first startup INFO log message
        app.logger.info('Riji startup')

    return app


@babel.localeselector
def get_locale():
    locale = request.accept_languages.best_match(current_app.config['LANGUAGES'])    
    # DEBUG translations
    # Either set language preference of browser
    # or forse language by uncommenting one of the following:
    #| locale = 'es' # Debug Spanish translation
    #| locale = 'de' # Debug German translation
    return locale


# Import models 
# have to be imported at the end to avoid circular imports
from app import models
    

## fin.
