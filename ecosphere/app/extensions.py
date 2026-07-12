"""
Centralized Flask extension instances.
Imported by the app factory and by models/routes to avoid circular imports.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
mail = Mail()
bcrypt = Bcrypt()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per hour"])
