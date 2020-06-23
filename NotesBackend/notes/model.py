from sqlalchemy import func
from notes.db import db


class NotesModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # username = db.Column(db.String(50))
    text = db.Column(db.String)
    time_created = db.Column(db.DateTime, server_default=func.now())
    time_modified = db.Column(db.DateTime, onupdate=func.now(), nullable=True)
