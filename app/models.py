# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from . import login_manager
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app
from datetime import datetime


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENT = 0x08
    ADMINISTER = 0x80


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def insert_roles():
        roles = {
            'User': (
                Permission.FOLLOW |
                Permission.COMMENT |
                Permission.WRITE_ARTICLES, True
            ),
            'Manager': (
                Permission.FOLLOW |
                Permission.COMMENT |
                Permission.WRITE_ARTICLES |
                Permission.MODERATE_COMMENT, False
            ),
            'Administer': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class Meet(db.Model):
    __tablename__ = 'meets'
    user_sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    user_affirmant_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    confirmed = db.Column(db.Integer, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_timestamp = db.Column(db.DateTime, default=None)

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        from sqlalchemy.exc import IntegrityError
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            u2 = User.query.offset(randint(0, user_count - 1)).first()
            m = Meet(sender=u,
                     affirmant=u2,
                     timestamp=forgery_py.date.date(True))
            db.session.add(m)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    nickname = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    ban = db.Column(db.Boolean, default=False)
    confirmed = db.Column(db.Boolean, default=False)

    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    meet_sender = db.relationship('Meet',
                                     foreign_keys=[Meet.user_sender_id],
                                     backref=db.backref('sender', lazy='joined'),
                                     lazy='dynamic',
                                     cascade='all, delete-orphan')
    meet_affirmant = db.relationship('Meet',
                                     foreign_keys=[Meet.user_affirmant_id],
                                     backref=db.backref('affirmant', lazy='joined'),
                                     lazy='dynamic',
                                     cascade='all, delete-orphan')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.nickname

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['TYKNOW_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed, randint
        import forgery_py

        seed()
        for i in range(count):
            u = User(
                nickname=forgery_py.internet.user_name(True),
                password=forgery_py.lorem_ipsum.word(),
                score=randint(1, 200) * 10
            )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser
