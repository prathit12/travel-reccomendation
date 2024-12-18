# -*- coding: utf-8 -*-

from flask import Flask
from elasticsearch import Elasticsearch

# Initialize Flask app
def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize Elasticsearch
    app.elasticsearch = Elasticsearch(app.config['ELASTICSEARCH_URL'])

    with app.app_context():
        # Import routes
        from . import routes
        return app