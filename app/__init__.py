from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from elasticsearch import Elasticsearch

app = Flask(__name__)
app.config.from_object(Config)
app.elasticsearch = Elasticsearch([app.config['ELASTIC_SEARCH_URL']]) \
    if app.config['ELASTIC_SEARCH_URL'] else None
db = SQLAlchemy(app)
migrate = Migrate(app, db)
socketio = SocketIO(app)

from app.api import bp as api_bp

app.register_blueprint(api_bp, url_prefix="/api")

from app import routes, models, errors, search
from app.api import *
