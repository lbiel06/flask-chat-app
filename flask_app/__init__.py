from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO


# Settings

class Config:
    SECRET_KEY = '123'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    

# Setup

app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)

socketio = SocketIO(app)


# Override Jinja delimeters to avoid colissions with
# Vue markup system

...


# Views

from . import views
