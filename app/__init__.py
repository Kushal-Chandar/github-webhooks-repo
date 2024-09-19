from flask import Flask
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)

    from .webhook.routes import webhook
    from .routes import root
    app.register_blueprint(webhook)
    app.register_blueprint(root)

    return app
