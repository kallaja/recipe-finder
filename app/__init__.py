from .config import Config
from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_wtf.csrf import CSRFProtect
from .models import Base, User
from .db import init_db
from .extensions import login_manager, sqlalchemy_db

# configure Flask-login
login_manager.login_view = 'auth.login'  # Redirect to 'auth.login' when login is required
login_manager.login_message_category = 'info'

db_file = Config.db_file


def create_app():
    # Create the Flask app
    app = Flask(__name__)
    app.app_context().push()
    app.config['SESSION_COOKIE_SECURE'] = True

    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.SCM_DO_BUILD_DURING_DEPLOYMENT = 1
    Bootstrap5(app)

    # CSRF Protection
    csrf = CSRFProtect(app)
    csrf.init_app(app)

    # Initialize the sqlite database for API responses
    init_db()

    # init database for user authentication
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
    sqlalchemy_db.init_app(app)

    login_manager.init_app(app)

    from .routes import main_bp, auth_bp

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    # create database tables
    with app.app_context():
        sqlalchemy_db.create_all()

    return app
