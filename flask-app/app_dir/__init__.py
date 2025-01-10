from flask import Flask
from .routes import main_routes, namizu_routes, gamechanger_routes
import logging

def create_app():
    time_format = "%Y-%m-%d %H:%M:%S"
    logging.basicConfig(filename='database/logfile.log', level=logging.DEBUG, format='[%(asctime)s] %(levelname)s %(name)s : %(message)s', datefmt=time_format)
    app = Flask(__name__)
    with open("flask_secret","r") as f:
        stringg = f.readline()
    app.config['SECRET_KEY'] = stringg
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400
    app.logger.debug("Secret key aquired")
    # Register blueprints
    app.register_blueprint(main_routes.bp)
    app.register_blueprint(namizu_routes.bp, url_prefix="/namizu")
    app.register_blueprint(gamechanger_routes.bp, url_prefix="/gamechanger")

    return app
