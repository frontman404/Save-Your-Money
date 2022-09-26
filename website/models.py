from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float)
    date = db.Column(db.Date)
    tag_id = db.Column(db.Integer, db.ForeignKey("etag.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class Etag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    expenses = db.relationship("Expense")


class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float)
    date = db.Column(db.Date)
    tag_id = db.Column(db.Integer, db.ForeignKey("itag.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    

class Itag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    incomes = db.relationship("Income")


class Saving(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float)
    date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(150))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    savings_goal = db.Column(db.Float)
    expenses = db.relationship("Expense")
    etags = db.relationship("Etag")
    incomes = db.relationship("Income")
    itags = db.relationship("Itag")
    savings = db.relationship("Saving")
    notes = db.relationship("Note")


