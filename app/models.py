# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from . import db, qiniu_store
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from . import login_manager
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app, request
from datetime import datetime
import hashlib
from markdown import markdown
import bleach


class Permission:
    FOLLOW = 0x01  # 关注
    COMMENT = 0x02  # 评论
    WRITE_ARTICLES = 0x04  # 发布文章
    MODERATE_COMMENT = 0x08  # 修改评论(管理员)
    ADMINISTER = 0x80  # 总舵主


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


class VRole(db.Model):
    # 认证
    __tablename__ = 'vroles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False)

    users = db.relationship('User', backref='vrole', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def insert_vroles():
        vroles = {
            'student': False,
            'teacher': False
        }
        for r in vroles:
            vrole = VRole.query.filter_by(name=r).first()
            if vrole is None:
                vrole = VRole(name=r)
            db.session.add(vrole)
        db.session.commit()


class Banning(db.Model):
    # 封禁理由
    __tablename__ = 'bannings'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True)
    body = db.Column(db.String(128))

    # questions = db.relationship()


class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # ban = db.Column(db.)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    answers = db.relationship('Answer', backref='q_answer', lazy='dynamic')
    focus_by = db.relationship('Focus', backref='focus_on', lazy='dynamic')

    def is_focus_by(self, user):
        return self.focus_by.filter_by(user_id=user.id).first() is not None

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'br', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))
db.event.listen(Question.body, 'set', Question.on_changed_body)


class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    answerer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    belong = db.Column(db.Integer, db.ForeignKey('questions.id'))

    voters = db.relationship('Vote', backref='voter', lazy='dynamic')
    comments = db.relationship('Comment', backref='answer', lazy='dynamic')

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'br', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))
db.event.listen(Answer.body, 'set', Answer.on_changed_body)


class Vote(db.Model):
    __tablename__ = 'votes'
    voter_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    voted_answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Focus(db.Model):
    __tablename__ = 'focuses'
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    answerer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'br', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))
db.event.listen(Comment.body, 'set', Comment.on_changed_body)


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

    avatat_hash = db.Column(db.String(32))

    # 身份认证
    real_name = db.Column(db.String(32))
    stu_number = db.Column(db.String(11), unique=True, index=True)

    # 储存图片的文件名, 用文件名获取URL
    photo_stu = db.Column(db.String(64))
    photo_idcard = db.Column(db.String(64))
    photo_head = db.Column(db.String(64))

    # 提交认证
    # vrole_verified = db.Column(db.Boolean)
    photos_uploaded = db.Column(db.Boolean)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    vrole_id = db.Column(db.Integer, db.ForeignKey('vroles.id'))

    questions = db.relationship('Question', backref='author', lazy='dynamic')
    answers = db.relationship('Answer', backref='answerer', lazy='dynamic')
    voted_answers = db.relationship('Vote', backref='voted_answer', lazy='dynamic')
    focus_on = db.relationship('Focus', backref='focus_by', lazy='dynamic')

    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
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
        if self.email is not None and self.avatat_hash is None:
            self.avatat_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

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
        self.follow(self)
        return True

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://gravatar.com/avatar'
        hash = self.avatat_hash or \
               hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, default=default, rating=rating, size=size)

    def vote_answer(self, answer):
        vote = self.voted_answers.filter_by(voted_answer_id=answer.id).first()
        if vote is None:
            vote = Vote(voted_answer=self, voter=answer)
            db.session.add(vote)
            return True
        else:
            db.session.delete(vote)
            return False

    def is_voted(self, answer):
        if self.voted_answers.filter_by(voted_answer_id=answer.id).first() is None:
            return False
        else:
            return True

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def focus(self, question):
        if not self.is_focus(question):
            f = Focus(focus_by=self, focus_on=question)
            db.session.add(f)

    def unfocus(self, question):
        f = self.focus_on.filter_by(question_id=question.id).first()
        if f:
            db.session.delete(f)

    def is_focus(self, question):
        return self.focus_on.filter_by(question_id=question.id).first() is not None

    def is_student(self):
        if self.vrole is None:
            return False
        return self.vrole.name == 'student'

    def is_teacher(self):
        if self.vrole is None:
            return False
        return self.vrole.name == 'teacher'

    def is_verified(self):
        return self.vrole is not None

    @staticmethod
    def get_photo_url(filename):
        return qiniu_store.url(filename)

    @property
    def followed_answers(self):
        return Answer.query.join(Follow, Follow.followed_id == Answer.answerer_id)\
            .filter(Follow.follower_id == self.id)

    @property
    def followed_questions(self):
        return Question.query.join(Follow, Follow.followed_id == Question.author_id)\
            .filter(Follow.follower_id == self.id)

    # @property
    # def followed_voted_answers(self):
    #    return Answer.query.join

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

    def is_verified(self):
        return False

login_manager.anonymous_user = AnonymousUser
