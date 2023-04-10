from flask import Flask, session
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

login_manager = LoginManager()

"""
These object can be used throughout project.
1.) Objects from this file can be included in many blueprints
2.) Isolating these object definitions avoids duplication and circular dependencies
"""

# Setup of key Flask object (app)
app = Flask(__name__)
app.secret_key = b'1673899960791b5e986de1781b77326d901c885d03a804a236d38ab6c8c00b1f'
login_manager.init_app(app)
# Setup SQLAlchemy object and properties for the database (db)
#dbURI = 'sqlite:///volumes/sqlite.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SQLALCHEMY_DATABASE_URI'] = dbURI
#app.config['SECRET_KEY'] = 'SECRET_KEY'
#db = SQLAlchemy()
#Migrate(app, db)
cors = CORS(app, resources={r"/": {"origins": "*"}})

# Images storage
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # maximum size of uploaded content
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']  # supported file types
#app.config['UPLOAD_FOLDER'] = 'volumes/uploads/'  # location of user uploaded content
