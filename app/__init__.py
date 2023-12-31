from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import Blueprint

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

from .models import User
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

from .main import main as main_blueprint
app.register_blueprint(main_blueprint)

#login_manager.init_app(app)

from app import models