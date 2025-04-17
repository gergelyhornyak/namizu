from flask import Flask
from .routes import main_routes, namizu_routes
from .routes import namizu_routes_new, main_routes_new
import logging
from datetime import timedelta


def create_app():
    time_format = "%Y-%m-%d %H:%M:%S"
    #logging.basicConfig(filename='database/logfile.log', level=logging.DEBUG, format='[%(asctime)s] %(levelname)s %(name)s : %(message)s', datefmt=time_format)
    app = Flask(__name__)
    with open("flask_secret","r") as f:
        stringg = f.readline()
    app.config['SECRET_KEY'] = stringg
    app.logger.debug("Secret key aquired")
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400
    app.permanent_session_lifetime = timedelta(weeks=1)
    app.logger.debug("Session lifetime set to 24hrs")
    # Register blueprints
    app.register_blueprint(main_routes_new.bp)
    app.register_blueprint(namizu_routes_new.bp, url_prefix="/namizu")

    return app
