from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from .models import Base
from flask_bootstrap import Bootstrap5
from flask_wtf.csrf import CSRFProtect

login_manager = LoginManager()
sqlalchemy_db = SQLAlchemy(model_class=Base)
csrf = CSRFProtect()
bootstrap = Bootstrap5()
