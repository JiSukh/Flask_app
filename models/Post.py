from app import db
from utils import Sym_Encryption

from flask import request
from flask_login import current_user

from sqlalchemy import event, desc

from datetime import datetime

import logging

logger = logging.getLogger('logger')

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

    @staticmethod
    def delete(post_id):
        post = db.session.query(Post).filter_by(id=post_id).first()
        db.session.delete(post)
        db.session.flush()
        db.session.commit()


    @staticmethod
    def create_post(author_user, title, body):
        post = Post(author_user.id, title,body)
        post = Sym_Encryption.encrypt_post(author_user,post)

        db.session.add(post)
        db.session.flush()
        db.session.commit()

    @staticmethod
    def get_all_posts(number = None):
        if not number:
            return Post.query.order_by(desc('id')).all()
        else:
            return Post.query.order_by(desc('id')).limit(number).all()
    
    @staticmethod
    def get_post(postid):
        return Post.query.filter_by(id=postid).first()



@event.listens_for(Post, 'after_insert')
def log_create_post(mapper, connection, target):
    logger.info(f'[User:{current_user.email}, Role:{current_user.role}, Post ID: {target.id}, IP:{request.remote_addr}] Post created.')


@event.listens_for(Post, 'after_update')
def log_update_post(mapper, connection, target):
    logger.info(f'[User:{current_user.email}, Role:{current_user.role}, Post ID: {target.id}, IP:{request.remote_addr}, Poster Email: {target.user.email}] Post updated.')


@event.listens_for(Post, 'after_delete')
def log_delete_post(mapper, connection, target):
    logger.info(f'[User:{current_user.email}, Role:{current_user.role}, Post ID: {target.id}, IP:{request.remote_addr}, Poster Email: {target.user.email}] Post deleted.')

