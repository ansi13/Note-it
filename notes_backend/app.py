from flask import Flask
from flask_restx import Api
from flask_migrate import Migrate


migrate = Migrate()


def create_app():
    from notes_backend.api_namespace import api_namespace
    from notes_backend.db import db, db_config

    app = Flask(__name__)
    api = Api(app, version='0.1', title='Notes Backend API',
              description='Backend API for Notes App')

    app.config['RESTPLUS_MASK_SWAGGER'] = False
    app.config.update(db_config)
    db.init_app(app)
    migrate.init_app(app, db)
    app.app_context().push()
    db.create_all()

    api.add_namespace(api_namespace)
    return app
