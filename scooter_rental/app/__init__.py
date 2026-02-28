from flask import Flask
from .config import Config
from .extensions import db, migrate, login_manager


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from .auth.routes import auth_bp
    from .web.routes import web_bp
    from .api.routes import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    return app
