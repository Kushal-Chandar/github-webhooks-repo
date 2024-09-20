from flask import Flask
from dotenv import load_dotenv
from flask.logging import default_handler
import logging

load_dotenv()


def create_app():
    logFormatter = logging.Formatter("%(asctime)s-%(levelname)s:%(name)s-%(message)s")
    fileHandler = logging.FileHandler("app.log")
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(logging.DEBUG)

    app = Flask(__name__)

    from .webhook.routes import webhook
    from .routes import root

    app.register_blueprint(webhook)
    app.register_blueprint(root)

    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(fileHandler)

    return app
