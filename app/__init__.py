from .config import Config
from flask import Flask
from .models import Base, User
from .db_api_responses import init_db
from .extensions import login_manager, sqlalchemy_db, csrf, bootstrap
from flask_session import Session


def create_app() -> Flask:
    """
    Creates and configures the Flask application.
    :return: The Flask application instance.
    """
    app = Flask(__name__)
    app.config.update(
        SCM_DO_BUILD_DURING_DEPLOYMENT=1,
        SECRET_KEY=Config.SECRET_KEY,
        WTF_CSRF_SECRET_KEY=Config.WTF_CSRF_SECRET_KEY,
        SQLALCHEMY_DATABASE_URI=Config.SQLALCHEMY_DATABASE_URI,
    )
    app.config['SESSION_COOKIE_SECURE'] = True  # # Cookies only via HTTPS
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["REMEMBER_COOKIE_SECURE"] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_TYPE'] = 'sqlalchemy'
    app.config['SESSION_SQLALCHEMY'] = sqlalchemy_db
    app.config['SESSION_PERMANENT'] = False

    # Initialize the database
    init_db()

    # Initialize Flask extensions
    sqlalchemy_db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    csrf.init_app(app)
    Session(app)

    # configure Flask-login
    login_manager.login_view = 'auth.login'  # Redirect to 'auth.login' when login is required
    login_manager.login_message_category = 'info'

    # Register blueprints
    from .routes import main_bp, auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    # create database tables
    with app.app_context():
        sqlalchemy_db.create_all()

    return app
