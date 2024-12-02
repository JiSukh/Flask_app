from app import db
from datetime import datetime


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