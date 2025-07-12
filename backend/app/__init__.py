"""
Application factory for the StackIt backend.
Everything – config, extensions, blueprints – is wired up here.
"""

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

from .extensions import db, jwt, limiter, socketio

migrate = Migrate()

def create_app() -> Flask:
    load_dotenv()  # Load environment variables from .env

    app = Flask(__name__)

    app.config.update(
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URI", "sqlite:///stackit.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", "super-secret"),  # Change in prod
    )

    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    migrate.init_app(app, db)
    CORS(app)

    from . import models  # noqa: F401

    from .blueprints.questions import questions_bp
    from .blueprints.notifications import bp as notifications_bp
    from .blueprints.auth import bp as auth_bp
    from .blueprints.answers import answers_bp
    from .blueprints.votes import votes_bp
    from .blueprints.tags import tags_bp
    from .blueprints.admin import admin_bp

    app.register_blueprint(questions_bp, url_prefix="/api/questions")
    app.register_blueprint(notifications_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(answers_bp, url_prefix="/api/answers")
    app.register_blueprint(votes_bp, url_prefix="/api/votes")
    app.register_blueprint(tags_bp, url_prefix="/api/tags")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    @app.errorhandler(404)
    def not_found(_):
        return {"error": "Not Found"}, 404

    return app
