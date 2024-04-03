from .database import db
from flask_security import UserMixin, RoleMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
import datetime
from sqlalchemy import ForeignKey, func
from sqlalchemy import DateTime, func, DATE


roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary = roles_users, backref=db.backref('users', lazy = 'dynamic'))


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80), unique = True)
    description = db.Column(db.String(255))


class Section(db.Model):
    __tablename__ = 'section'
    sec_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sec_name = db.Column(db.String(255), unique = True, nullable = False)
    doc = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False) # date of creation
    desc = db.Column(db.String(255))

class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable = False)
    sec_id = db.Column(db.Integer, ForeignKey("section.sec_id")) 
    download_path = db.Column(db.String(255))

class BooksUsers(db.Model):
    __tablename__ = 'books_users'
    bu_id = db.Column(db.Integer, primary_key= True, autoincrement=True)
    book_id = db.Column(db.Integer, ForeignKey("book.id"))
    user_id = db.Column(db.Integer, ForeignKey("user.id"))
    issue_date = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    return_date = db.Column(db.Date, nullable=False) 
    isApproved = db.Column(db.Integer, nullable = False, default = 0)
    isReturned = db.Column(db.Integer, nullable = False, default = 0)
    isRejected = db.Column(db.Integer, nullable = False, default = 0)
    feedback = db.Column(db.String(255))

