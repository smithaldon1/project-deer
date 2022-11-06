import os
from flask import Flask, render_template
from flask_mail import Mail
from celery import Celery
from config import Config
import logging
from jinja2 import ChoiceLoader, FileSystemLoader
from flask.logging import default_handler
from logging.handlers import RotatingFileHandler
import firebase_admin
from firebase_admin import credentials, firestore
from authorizenet import apicontractsv1


### Flask extension objects instantiation ###
mail = Mail()

### Instantiate Firebase ###
cred = credentials.Certificate(Config.FIREBASE_CRED)
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()

### Instantiate Merchant Auth ###
merchantAuth = apicontractsv1.merchantAuthenticationType()
merchantAuth.name = Config.API_LOGIN_ID
merchantAuth.transactionKey = Config.TRANSACTION_KEY

### Instantiate Celery ###
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL, result_backend=Config.RESULT_BACKEND)

### Application Factory ###
def create_app():
    app = Flask(__name__)
    
    # Configure Flask App Instance
    CONFIG_TYPE = os.getenv('CONFIG_TYPE', default='config.DevelopmentConfig')
    app.config.from_object(CONFIG_TYPE)
    
    # Configure celery
    celery.conf.update(app.config)
    
    # Register blueprints
    register_blueprints(app)
    
    # Initialize flask extension objects
    initialize_extensions(app)
    
    # Configure logging
    configure_logging(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Overwrite Flask jinja_loader, using ChoiceLoader
    template_loader = ChoiceLoader([
        app.jinja_loader,
        FileSystemLoader('static'),
    ])
    
    return app
    
### Helper Functions ### 
def register_blueprints(app):
    from app.main import main_blueprint
    from app.payment import payment_blueprint
    
    app.register_blueprint(payment_blueprint, url_prefix='/donate')
    app.register_blueprint(main_blueprint)
    
def initialize_extensions(app):
    mail.init_app(app)
    
def register_error_handlers(app):
    # 400 – Bad Request
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('400.html'), 400
    
    # 403 – Forbidden
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403
    
    # 404 – Page Not Found
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    # 404 – Method Not Allowed
    @app.errorhandler(405)
    def method_not_allowed(e):
        return render_template('405.html'), 405
    
    # 500 – Internal Server Error
    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500

def configure_logging(app):
    # Deactivate the default flask logger so that log messages do not get duplicated
    app.logger.removeHandler(default_handler)
    
    # Create a file handler object
    file_handler = RotatingFileHandler('flaskapp.log', maxBytes=16384, backupCount=20)
    
    # Set logging level of file handler object so it logs INFO & up
    file_handler.setLevel(logging.INFO)
    
    # Create file formatter object
    file_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(filename)s: %(lineno)d]')
    
    # Apply file formatter object to file handler
    file_handler.setFormatter(file_formatter)
    
    # Add file handler to logger
    app.logger.addHandler(file_handler)

