import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from cryptography.fernet import Fernet

# Add your project root to the path if necessary
sys.path.append('/path/to/your/project/root')

app = Flask(__name__)

# Configuration settings
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Supermarket.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Added to suppress warnings

# Encryption key for Fernet
# Note: The key should be saved and reused across app restarts for consistent encryption.
# You may need to read this key from a secure file or environment variable in production.
encryption_key = Fernet.generate_key()
app.config['ENCRYPTION_KEY'] = encryption_key

# Initialize Fernet with encryption key
fernet = Fernet(encryption_key)

# Initialize extensions
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

# Import routes and models
from . import routes, models
