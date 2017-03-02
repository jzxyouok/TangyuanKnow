# -*- coding: utf-8 -*-

from .. import photos
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField, StringField, SelectField
from wtforms.validators import DataRequired, Length, Regexp


class UploadForm(FlaskForm):
    photo = FileField(validators=[
        FileAllowed(photos, u'只能上传图片！'),
        FileRequired(u'文件未选择！')])
    submit = SubmitField(u'上传')


class StudentAuthForm(FlaskForm):
    stu_number = StringField(u'学号', validators=[Length(10, 10, u'学号应为10位数字!')])
    real_name = StringField(u'真实姓名', validators=[Length(1, 5),
                                                 Regexp(u'[\u4e00-\u9fa5]+', 0,
                                                        u'真实姓名仅限使用汉字!')])
    stu_photo = FileField(validators=[FileAllowed(photos, u'只能上传图片!'),
                                      FileRequired(u'请添加学生证照片!')])
    id_photo = FileField(validators=[FileAllowed(photos, u'只能上传图片!'),
                                     FileRequired(u'请添加身份证照片!')])
    submit = SubmitField(u'上传')
