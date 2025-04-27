from flask import Flask,session
from .routes import namizu_routes_new, main_routes_new
import logging
from datetime import timedelta


def create_app():   
    app = Flask(__name__)

    file_handler = logging.FileHandler('database/logfile.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s (in %(pathname)s:%(lineno)d)'))
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.DEBUG)

    with open("flask_secret","r") as f:
        stringg = f.readline()
    app.config['SECRET_KEY'] = stringg
    app.logger.debug("Secret key aquired")
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400
    app.permanent_session_lifetime = timedelta(weeks=1)
    app.logger.debug("Session lifetime set to 1 week")
    # Register blueprints
    app.register_blueprint(main_routes_new.bp)
    app.register_blueprint(namizu_routes_new.bp, url_prefix="/namizu")

    return app
