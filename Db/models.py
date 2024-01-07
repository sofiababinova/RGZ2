from . import db 
from flask_login import UserMixin


class users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(102), nullable=False)


class profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    type_of_service = db.Column(db.Text, nullable=False)
    experience = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    about_me = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=True)
