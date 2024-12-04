from flask import Flask, render_template, request, url_for, abort
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_admin import Admin
from flask_admin.menu import MenuLink
from flask_login import LoginManager
from flask_qrcode import QRcode

import logging
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
limiter = Limiter(get_remote_address)
login_manager = LoginManager()
qrcode = QRcode()


# Register blueprints
from accounts.views import accounts_bp
from posts.views import posts_bp
from security.views import security_bp

# Create the Flask application
def create_app():
    app = Flask(__name__)
    
    # Load configuration from config.py
    app.config.from_object(Config)
    
    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    login_manager.init_app(app)
    qrcode.init_app(app)

    # Register blueprints
    app.register_blueprint(accounts_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(security_bp)
    

    class MainIndexLink(MenuLink):
        def get_url(self):
            return url_for('index')

    # Setup Flask-Admin (can be configured more as needed)
    admin = Admin(app, name='DB Admin', template_mode='bootstrap4')
    from models.views import PostView, UserView
    from models.Post import Post
    from models.User import User
    admin._menu = admin._menu[1:] 
    admin.add_link(MainIndexLink(name='Home Page'))
    admin.add_view(PostView(Post, db.session))
    admin.add_view(UserView(User, db.session))


    app.route('/')(index)
    app.route("/favicon.ico")(favicon)
    app.errorhandler(Exception)(handle_error)
    app.before_request(check_for_admin)

    return app

def setup_logging():
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(Config.LOG_FILE_PATH, 'a')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s', '%d/%m/%Y %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

setup_logging()

# Routes
def index():
    return render_template("home/index.html")

def favicon():
    return "", 200

# Error handler
def handle_error(e):
    error_code = getattr(e, 'code', 500)

    if error_code == 403:
        logger = logging.getLogger('logger')
        logger.warning(f'[User:{current_user.email}, Role:{current_user.role}, IP:{request.remote_addr}, URL requested: {request.url}] Unauthorised access request.')
    return render_template(f'errors/{error_code}.html', error=e), error_code    

# Before request function
def check_for_admin(*args, **kw):
    if request.path.startswith('/admin'):
        if not hasattr(current_user, 'role'):
            abort(401)
        elif not current_user.role == 'db_admin':
            abort(403)
