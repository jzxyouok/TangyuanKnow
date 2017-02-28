# -*- coding: utf-8 -*-

from .. import photos
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField


class UploadForm(FlaskForm):
    photo = FileField(validators=[
        FileAllowed(photos, u'只能上传图片！'),
        FileRequired(u'文件未选择！')])
    submit = SubmitField(u'上传')


class StudentAuthForm(FlaskForm):
    stu_photo = FileField(validators=[FileAllowed(photos, u'只能上传图片!'),
                                      FileRequired(u'请添加学生证照片!')])
    id_photo = FileField(validators=[FileAllowed(photos, u'只能上传图片!'),
                                     FileRequired(u'请添加身份证照片!')])
    submit = SubmitField(u'上传')