from flask import Flask, abort, url_for, request
from datetime import datetime
#database improt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import MetaData, event
from datetime import datetime
# IMPORT BLUEPRINTS
from accounts.views import accounts_bp
from posts.views import posts_bp
from security.views import security_bp
#database admin stuff
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
#rate limit
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import secrets
#.env to hide keys
from flask_login import LoginManager, UserMixin, current_user
import logging
import os
import pyotp
from dotenv import load_dotenv
from flask_qrcode import QRcode



# captcha keys
load_dotenv()
RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_API_KEY')
RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_API_KEY')
maximum_login_attempt = 3


app = Flask(__name__)
app.config.from_object(__name__)


#rate limiting
limiter = Limiter(get_remote_address,app = app,default_limits=["20 per minute", "500 per day"])

qrcode = QRcode(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = '/login'
login_manager.login_message = "Please login to acces the page"
login_manager.login_message_category = 'info'


## Add blueprints

app.register_blueprint(accounts_bp)
app.register_blueprint(posts_bp)
app.register_blueprint(security_bp)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('./log/logs.log','a')
handler.setLevel(logging.DEBUG) 
formatter = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s', '%d/%m/%Y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)


app.config['SECRET_KEY'] = secrets.token_hex(16)

# DATABASE CONFIGURATION
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///csc2031blog.db'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASK_ADMIN_FLUID_LAYOUT'] = True

metadata = MetaData(
    naming_convention={
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
    }
)


db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db)


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.id'))
    created = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)
    user = db.relationship("User", back_populates="posts",)

    def __init__(self, userid, title, body):
        self.userid = userid
        self.created = datetime.now()
        self.title = title
        self.body = body

    def update(self, title, body):
        self.created = datetime.now()
        self.title = title
        self.body = body
        db.session.commit()


@event.listens_for(Post, 'after_insert')
def log_create_post(mapper, connection, target):
    logger.info(f'[User:{current_user.email}, Role:{current_user.role}, Post ID: {target.id}, IP:{request.remote_addr}] Post created.')


@event.listens_for(Post, 'after_update')
def log_update_post(mapper, connection, target):
    user = db.session.query(User).filter_by(id=target.userid).first()
    logger.info(f'[User:{current_user.email}, Role:{current_user.role}, Post ID: {target.id}, IP:{request.remote_addr}, Poster Email: {user.email}] Post updated.')


@event.listens_for(Post, 'after_delete')
def log_delete_post(mapper, connection, target):
    user = db.session.query(User).filter_by(id=target.userid).first()
    logger.info(f'[User:{current_user.email}, Role:{current_user.role}, Post ID: {target.id}, IP:{request.remote_addr}, Poster Email: {user.email}] Post deleted.')


class MainIndexLink(MenuLink):
     def get_url(self):
         return url_for('index')




class PostView(ModelView):
    column_display_pk = True  
    column_hide_backrefs = False
    column_list = ('id', 'userid', 'created', 'title', 'body', 'user')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'db_admin'
    
    def inaccessible_callback(self, name, **kwargs):
        abort(403)
        
class UserView(ModelView):
    column_display_pk = True  # optional, but I like to see the IDs in the list
    column_hide_backrefs = False
    column_list = ('id', 'email', 'password', 'firstname', 'lastname', 'phone', 'posts', 'mfa_enable', 'mfa_key')
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'db_admin'
    
    def inaccessible_callback(self, name, **kwargs):
        abort(403)

class LogView(ModelView):
    column_display_pk = True  # optional, but I like to see the IDs in the list
    column_hide_backrefs = False

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'db_admin'
    
    def inaccessible_callback(self, name, **kwargs):
        abort(403)

class Log(db.Model):
    __tablename__ = 'log'

    id = db.Column(db.Integer, primary_key=True)

    userid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reg_time = db.Column(db.DateTime, nullable=False)
    latest_login = db.Column(db.DateTime)
    previous_login = db.Column(db.DateTime)
    latest_ip = db.Column(db.String())
    previous_ip = db.Column(db.String())

    user = db.relationship("User", back_populates="log")

    def __init__(self, userid):
        self.userid = userid
        self.reg_time = datetime.now()

#users
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # User authentication information.
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    # User information
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    mfa_key = db.Column(db.Integer, nullable=False)
    mfa_enable = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean(), nullable=False, default=True)
    role = db.Column(db.String(), nullable=False, default='end_user')

    # User posts
    posts = db.relationship("Post", order_by=Post.id, back_populates="user")

    log = db.relationship("Log", uselist=False, back_populates="user")

    def __init__(self, email, firstname, lastname, phone, password, mfa_enable, mfa_key):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.phone = phone
        self.password = password
        self.mfa_key = mfa_key
        self.mfa_enable = mfa_enable
        self.role = 'end_user'

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    def verify_password(self, input_password):
        if self.password.strip() == input_password.strip():
            return True
        else:
            return False
        
    def verify_mfa_pin(self, input_pin):
        if pyotp.TOTP(self.mfa_key).verify(input_pin):
            return True
        else:
            return False
        
    def verify_mfa_enabled(self):
        if self.mfa_enable == 1:
            return True
        else:
            return False
        
    def generate_log(self, on_login = True):
        prev_log = Log.query.filter_by(userid=self.id).order_by(Log.id.desc()).first()
        new_log = Log(userid = self.id)
        if prev_log:
            new_log.reg_time = prev_log.reg_time
            new_log.previous_login = prev_log.latest_login
            new_log.previous_ip = prev_log.latest_ip

        if on_login:
            new_log.latest_login = datetime.now()
            new_log.latest_ip = request.remote_addr
            logger.info(f'[User:{current_user.email}, Role:{current_user.role}, IP:{request.remote_addr}] Valid Login Attempt.')

            
            
        

        db.session.add(new_log)
        db.session.commit()



@event.listens_for(User, 'after_insert')
def log_create_post(mapper, connection, target):
    logger.info(f'[User:{target.email}, Role:{target.role}, IP:{request.remote_addr}] Valid Registration.')
        
       

admin = Admin(app, name='DB Admin', template_mode='bootstrap4')
admin._menu = admin._menu[1:] 
admin.add_link(MainIndexLink(name='Home Page'))
admin.add_view(PostView(Post, db.session))
admin.add_view(UserView(User, db.session))

