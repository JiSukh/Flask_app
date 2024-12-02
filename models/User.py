from app import db, login_manager
from .Post import Post
from .Log import Log

from flask import request
from flask_login import UserMixin, current_user

from argon2.exceptions import VerifyMismatchError

from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

from datetime import datetime

import base64
import secrets
import pyotp
import logging
import argon2


logger = logging.getLogger('logger')

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # User authentication information.
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(999), nullable=False)

    # User information
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    mfa_key = db.Column(db.Integer, nullable=False)
    mfa_enable = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean(), nullable=False, default=True)
    role = db.Column(db.String(), nullable=False, default='end_user')
    salt = db.Column(db.String(100), nullable=False)

    # User posts
    posts = db.relationship("Post", order_by=Post.id, back_populates="user")

    log = db.relationship("Log", uselist=False, back_populates="user")

    def __init__(self, email, firstname, lastname, phone, password, mfa_enable, mfa_key):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.phone = phone
        self.password = password
        self.mfa_key = pyotp.random_base32()
        self.mfa_enable = mfa_enable
        self.role = 'end_user'
        self.salt = base64.b64encode(secrets.token_bytes(32)).decode()

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

        
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


    def update_user(self, new_firstname=None, new_lastname=None, new_phone=None, new_email=None):
        try:
            # check unique emal and email is not the same as current
            if new_email and new_email != self.email:
                if User.query.filter_by(email=new_email).first():
                    return False, "Email is already in use."

            #change fields.
            if new_firstname:
                self.firstname = new_firstname
            if new_lastname:
                self.lastname = new_lastname
            if new_phone:
                self.phone = new_phone
            if new_email:
                self.email = new_email

            db.session.commit()
            return True, "User updated successfully."
        
        except IntegrityError as e:
            db.session.rollback()
            return False, f"Database integrity error: {e.orig}"
        except Exception as e:
            db.session.rollback()
            return False, f"Error updating user: {str(e)}"
        

    def update_mfa(self, enable_mfa):
        self.mfa_enable = enable_mfa
        db.session.commit()


    @staticmethod
    def create_user(email, firstname, lastname, phone, password, mfa_enabled = False):
        
        ph = argon2.PasswordHasher()
        hash_pass = ph.hash(password)

        
        user = User(email=email,
                        firstname=firstname,
                        lastname=lastname,
                        phone=phone,
                        password= hash_pass,
                        mfa_enable = mfa_enabled
                        )
        
        db.session.add(user)
        db.session.commit()
        user.generate_log(on_login=False)
        return user



    @staticmethod
    def find_user_from_email(email):
        return User.query.filter(User.email.ilike(email)).first()
    
    @staticmethod
    def check_user_is_real(email):
        if User.query.filter(User.email.ilike(email)).first():
            return True
        return False
    

    @staticmethod
    def verify_password_against_email(email, entered_password):
        user = User.find_user_from_email(email)

        ph = argon2.PasswordHasher()
        try:
            return ph.verify(user.password, entered_password)
        except VerifyMismatchError:
            return False





@event.listens_for(User, 'after_insert')
def log_create_post(mapper, connection, target):
    logger.info(f'[User:{target.email}, Role:{target.role}, IP:{request.remote_addr}] Valid Registration.')