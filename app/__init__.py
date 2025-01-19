import sys
sys.path.append('/path/to/your/project/root')
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from cryptography.fernet import Fernet  # Added for encryption

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Supermarket.db'

# Encryption key for Fernet
encryption_key = Fernet.generate_key()
app.config['ENCRYPTION_KEY'] = encryption_key

# Initialize Fernet with encryption key
fernet = Fernet(encryption_key)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@app.after_request
def add_cache_control(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

from . import routes, models
