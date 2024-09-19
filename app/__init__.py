from flask import Flask
from flask_bootstrap import Bootstrap
from .db import init_db
from .routes import main_bp


def create_app():
    # Create the Flask app
    app = Flask(__name__)
    Bootstrap(app)

    # Initialize the database
    init_db()

    # Register the blueprint
    app.register_blueprint(main_bp)

    return app
