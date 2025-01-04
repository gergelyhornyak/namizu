from flask import Flask
from .routes import main_routes, askus_routes, gamechanger_routes
import logging

def create_app():
    time_format = "%Y-%m-%d %H:%M:%S"
    logging.basicConfig(filename='logfile.log', level=logging.DEBUG, format='[%(asctime)s] %(levelname)s %(name)s : %(message)s', datefmt=time_format)
    app = Flask(__name__)
    with open("flask_secret","r") as f:
        stringg = f.readline()
    app.config['SECRET_KEY'] = stringg#"mpuPR4CrqCOiPsse"#''.join(random.choices(string.ascii_letters + string.digits, k=32))
    app.logger.debug("Secret key aquired")
    # Register blueprints
    app.register_blueprint(main_routes.bp)
    app.register_blueprint(askus_routes.bp, url_prefix="/askus")
    app.register_blueprint(gamechanger_routes.bp, url_prefix="/gamechanger")

    return app
