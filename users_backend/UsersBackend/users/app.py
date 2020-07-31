from flask import Flask
from flask_restx import Api
from flask_migrate import Migrate


migrate = Migrate()


def create_app():
    from users.api_namespace import api_namespace

    app = Flask(__name__)
    api = Api(app, version='0.1', title='Users Authentication Backend API',
              description='Backend API for Notes App')

    from users.db import db, db_config
    app.config['RESTPLUS_MASK_SWAGGER'] = False
    app.config.update(db_config)
    db.init_app(app)
    app.db = db
    migrate.init_app(app, db)

    api.add_namespace(api_namespace)
    return app
