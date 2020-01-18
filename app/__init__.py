
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

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
from app import routes, models

# fin.
