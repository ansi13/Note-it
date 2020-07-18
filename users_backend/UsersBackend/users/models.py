from sqlalchemy import func
from users.db import db


class UserModel(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(100))
    time_created = db.Column(db.DateTime, server_default=func.now())
