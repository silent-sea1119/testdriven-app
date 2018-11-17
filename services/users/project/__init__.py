import os

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension

# instantiate the extensions
db = SQLAlchemy()
toolbar = DebugToolbarExtension()


def create_app(script_info=None):

    # instantiate the app
    app = Flask(__name__)

    # enabled CORS
    CORS(app)

    # set config
    app_settings = os.getenv("APP_SETTINGS")
    app.config.from_object(app_settings)

    # setup extensions
    db.init_app(app)
    toolbar.init_app(app)

    # register blueprints
    from project.api.users import users_blueprint

    app.register_blueprint(users_blueprint)

    # register context for flask cli
    @app.shell_context_processor
    def ctx():
        return {"app": app, "db": db}

    return app
