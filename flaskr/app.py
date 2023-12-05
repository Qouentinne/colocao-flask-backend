from flask import Flask
from dotenv import load_dotenv


def create_app(secret_key, db_uri):
    load_dotenv()
    app = Flask(__name__)
    app.secret_key = secret_key
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

    @app.route('/')
    def hello_world():
        return 'Hello, World!'
    
    return app



