import os
import logging
from logging.handlers import SMTPHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from logging.handlers import RotatingFileHandler
from flask_mail import Mail
from config import Config


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__, static_folder='static')
    app.config.from_object(config_class)

    # Import blueprint and routes.
    from app.errors import error, routes
    from app.main import main, routes
    from app.auth import auth, routes
    from app.blog import blog, routes

    # Blueprint registration.
    app.register_blueprint(error)
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(blog, url_prefix='/blog')

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:

            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None

            if app.config['MAIL_USE_TLS']:
                secure = ()
                
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr=app.config['ADMINS'],
                toaddrs=app.config['PERSONAL_EMAIL'], subject='Blog site error',
                credentials=auth, secure=secure)

            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        # LOCAL LOGS
        if not os.path.exists('logs'):
            # Create a log directory if dir does not exist.
            os.mkdir('logs')

        file_handler = RotatingFileHandler(
            'logs/blog.log', maxBytes=10240, backupCount=10)

        # Set format for log messages.
        # Timestamp, logging level, the message, the source file and its line number.
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))

        # Lower the logging level and application logger to the INFO Category.
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Blog site startup.')

    return app


from . import models