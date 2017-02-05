# -*- coding: utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf8')

from ..models import Role, User
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError


class EditProfileForm(FlaskForm):
    name = StringField('姓名', validators=[Length(1, 64)])
    location = StringField('位置', validators=[Length(1, 64)])
    about_me = TextAreaField('个人简介')
    submit = SubmitField('提交')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Regexp('[A-Za-z0-9_.]+@qq.com', 0, '抱歉，目前仅支持QQ邮箱')])
    nickname = StringField('昵称', validators=[DataRequired(), Length(1, 64),
                                             Regexp('[^\x00-\xffa-zA-Z0-9]+',
                                                    0, '用户昵称仅限使用汉字、字母和数字')])
    confirmed = BooleanField('邮件认证')
    role = SelectField('角色', coerce=int)
    name = StringField('姓名', validators=[Length(0, 64)])
    location = StringField('位置', validators=[Length(0, 64)])
    about_me = TextAreaField('个人简介')
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被占用.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(nickname=field.data).first():
            raise ValidationError('昵称已被占用.')
