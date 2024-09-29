from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from .models import Base

login_manager = LoginManager()
sqlalchemy_db = SQLAlchemy(model_class=Base)
