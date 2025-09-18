
import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Configure for Replit proxy environment
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration - PostgreSQL with Supabase
DATABASE_URL = os.environ.get("DATABASE_URL")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_DB_URL = os.environ.get("SUPABASE_DB_URL")

if DATABASE_URL:
    # Use PostgreSQL (Supabase or other)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
elif SUPABASE_DB_URL:
    # Use Supabase PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = SUPABASE_DB_URL
else:
    # Fallback to SQLite for local development
    basedir = os.path.abspath(os.path.dirname(__file__))
    instance_dir = os.path.join(basedir, 'instance')
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_dir, "app.db")}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

# Import routes
import routes
