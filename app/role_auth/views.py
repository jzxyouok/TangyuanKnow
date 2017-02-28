# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os
from . import role_auth
from .. import photos, qiniu_store, db
from .forms import UploadForm, StudentAuthForm
from flask import Flask, render_template, current_app, redirect, flash, url_for
from flask_login import current_user, login_required
from ..decorators import permission_required, admin_required


@role_auth.route('/upload-file', methods=['GET', 'POST'])
@admin_required  # 测试使用
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        ret, info = qiniu_store.save(form.photo.data)
        if ret is not None:
            file_url = qiniu_store.url(ret['key'])
        else:
            print info
            file_url = '#'
    else:
        file_url = None
    return render_template('role_auth/upload.html', form=form, file_url=file_url)


@role_auth.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = StudentAuthForm()
    id_url, stu_url = None, None
    if current_user.photo_idcard is not None \
        and current_user.photo_stu is not None:
        id_url = qiniu_store.url(current_user.photo_idcard)
        stu_url = qiniu_store.url(current_user.photo_stu)
    if form.validate_on_submit():
        id_ret, id_info = qiniu_store.save(form.id_photo.data)
        stu_ret, stu_info = qiniu_store.save(form.stu_photo.data)
        if id_ret is not None and stu_ret is not None:
            # id_url = qiniu_store.url(id_ret['key'])
            # stu_url = qiniu_store.url(stu_ret['key'])

            current_user.photo_stu = stu_ret['key']
            current_user.photo_idcard = id_ret['key']
            current_user.photos_uploaded = True
            db.session.add(current_user)
            db.session.commit()
            flash('上传成功,请耐心等待管理员审核.')
        else:
            flash('上传有误!')
        return redirect(url_for('role_auth.upload'))
    return render_template('role_auth/index.html', form=form, id_url=id_url, stu_url=stu_url)


@role_auth.route('/')
@login_required
def index():
    if current_user.is_student():
        return 'Hi, Student!'
    elif current_user.is_teacher():
        return 'Hi, Teacher!'
    return redirect(url_for('role_auth.upload'))


@role_auth.route('/admin')
@admin_required
def admin():
    pass

