# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log in')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Regexp('[A-Za-z0-9_.]+@qq.com', 0, '抱歉，目前仅支持QQ邮箱')])
    nickname = StringField('昵称', validators=[DataRequired(), Length(1, 64),
                                             Regexp('[^\x00-\xffa-zA-Z0-9]+',
                                                    0, '用户昵称仅限使用汉字、字母和数字')])
    password = PasswordField('密码', validators=[DataRequired(), EqualTo('password2', '两次密码不一致')])
    password2 = PasswordField('密码确认', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已被注册。')

    def validate_nickname(self, field):
        if User.query.filter_by(nickname=field.data).first():
            raise ValidationError('用户名已被占用，换一个试试吧！')
