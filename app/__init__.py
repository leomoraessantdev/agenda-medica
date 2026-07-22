"""Application factory da Agenda Medica."""
from flask import Flask

from app.config import get_config
from app.extensions import db
from app.utils.logging import configure_logging
from app.utils.security import generate_csrf_token


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    configure_logging(app)
    db.init_app(app)
    app.jinja_env.globals["csrf_token"] = generate_csrf_token

    _register_blueprints(app)
    _register_error_handlers(app)

    return app


def _register_blueprints(app: Flask) -> None:
    from app.blueprints.agenda.routes import agenda_bp
    from app.blueprints.auth.routes import auth_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(agenda_bp)


def _register_error_handlers(app: Flask) -> None:
    from app.errors.handlers import register_error_handlers

    register_error_handlers(app)
