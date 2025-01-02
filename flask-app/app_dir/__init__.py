from flask import Flask
from .routes import main_routes, askus_routes, gamechanger_routes
import random
import string

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "mpuPR4CrqCOiPsse"#''.join(random.choices(string.ascii_letters + string.digits, k=32))

    # Register blueprints
    app.register_blueprint(main_routes.bp)
    app.register_blueprint(askus_routes.bp, url_prefix="/askus")
    app.register_blueprint(gamechanger_routes.bp, url_prefix="/gamechanger")

    return app
