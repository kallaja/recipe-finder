from .config import Config
from flask import Flask
from .models import Base, User
from .db import init_db
from .extensions import login_manager, sqlalchemy_db, csrf, bootstrap
from flask_session import Session

# configure Flask-login
login_manager.login_view = 'auth.login'  # Redirect to 'auth.login' when login is required
login_manager.login_message_category = 'info'

db_file = Config.response_db_file


def create_app():
    # Create the Flask app
    app = Flask(__name__)
    app.config.update(
        SCM_DO_BUILD_DURING_DEPLOYMENT=1,
        SECRET_KEY=Config.SECRET_KEY,
        WTF_CSRF_SECRET_KEY=Config.WTF_CSRF_SECRET_KEY,
        SQLALCHEMY_DATABASE_URI=Config.SQLALCHEMY_DATABASE_URI,
    )
    app.config['SESSION_COOKIE_SECURE'] = True  # Ensures cookies are sent over HTTPS
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["REMEMBER_COOKIE_SECURE"] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Mitigates CSRF attacks
    app.config['SESSION_TYPE'] = 'sqlalchemy'
    app.config['SESSION_FILE_DIR'] = Config.SESSION_FILE_DIR  # Set your session file path
    app.config['SESSION_PERMANENT'] = False

    # Initialize the sqlite database for API responses
    init_db()

    sqlalchemy_db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    csrf.init_app(app)
    Session(app)

    from .routes import main_bp, auth_bp

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    # create database tables
    with app.app_context():
        sqlalchemy_db.create_all()

    return app
