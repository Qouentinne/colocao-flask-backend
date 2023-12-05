import models
from app import create_app
from api import create_api
from db import db
import os
from dotenv import load_dotenv
import urllib.parse

# CONFIG
load_dotenv()
db_uri = 'postgresql://'+os.getenv('SUPABASE_USER')+':'+os.getenv(urllib.parse.quote_plus('SUPABASE_PWD'))+'@'+os.getenv('SUPABASE_HOST')+':5432/postgres'

app = create_app(secret_key = os.getenv('SECRET_KEY'), db_uri = db_uri)
db.init_app(app)
with app.app_context():
    db.create_all()
    models.BaseModel.metadata.create_all(db.engine)

api = create_api(app)

if __name__ == '__main__':
    app.run(debug=(os.getenv('ENVIRONMENT')!='PRODUCTION'), host="0.0.0.0", port=5000)
