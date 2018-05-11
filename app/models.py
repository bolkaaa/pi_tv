from datetime import datetime

from database import db
from flask_security import RoleMixin,  UserMixin


roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    folder = db.Column(db.String(16), unique=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    name = db.Column(db.String(255))
    roles = db.relationship(
        'Role',
        secondary=roles_users,
        backref=db.backref('users', lazy='dynamic')
    )


class LoopMedia(db.Model):
    __tablename__ = 'loop_media'

    id = db.Column(db.Integer, primary_key=True)
    media_id = db.Column(db.Integer(), db.ForeignKey('media.id'))
    loop_id = db.Column(db.Integer(), db.ForeignKey('loop.id'))
    interval = db.Column(db.Integer(), default=5)
    position = db.Column(db.Integer(), default=0)
    media = db.relationship("Media")


class Loop(db.Model):
    __tablename__ = 'loop'

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    title = db.Column(db.String(255))
    folder = db.Column(db.String(16), unique=True)
    active = db.Column(db.Boolean(), default=0)
    media = db.relationship(
        "LoopMedia", order_by='LoopMedia.position')


class Media(db.Model):
    __tablename__ = 'media'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    title = db.Column(db.String(255))
    filename = db.Column(db.String(32))
    type = db.Column(db.String(50))
    url = db.Column(db.String(255), default='')
    video_id = db.Column(db.String(128), default='')
    uploaded = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    deleted = db.Column(db.Boolean(), default=False)

    def __str__(self):
        return self.filename
