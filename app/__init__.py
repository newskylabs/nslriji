
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Application
app = Flask(__name__)

# Use the application config
app.config.from_object(Config)

# Database
db = SQLAlchemy(app)

# Database migration engine
migrate = Migrate(app, db)

# Routes and models 
# have to be imported at the end to avoid circular imports
from app import routes, models

# fin.
