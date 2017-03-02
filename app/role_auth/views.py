# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os
from . import role_auth
from .. import photos, qiniu_store, db
from ..email import send_email
from .forms import UploadForm, StudentAuthForm
from flask import Flask, render_template, current_app, redirect, flash, url_for, request
from flask_login import current_user, login_required
from ..decorators import permission_required, admin_required
from ..models import User, VRole


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
    if not current_user.is_verified() and current_user.photos_uploaded:
        # 仅当未认证且已经提交了证明图片时才显示这些图片
        id_url = qiniu_store.url(current_user.photo_idcard)
        stu_url = qiniu_store.url(current_user.photo_stu)
    if form.validate_on_submit():
        id_ret, id_info = qiniu_store.save(form.id_photo.data)
        stu_ret, stu_info = qiniu_store.save(form.stu_photo.data)
        if id_ret is not None and stu_ret is not None:
            # id_url = qiniu_store.url(id_ret['key'])
            # stu_url = qiniu_store.url(stu_ret['key'])
            current_user.real_name = form.real_name.data
            current_user.stu_number = form.stu_number.data
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
    User.query.filter_by(photos_uploaded=True, vrole_id=None).all()
    page = request.args.get('page', 1, type=int)
    pagination = User.query.filter_by(photos_uploaded=True, vrole_id=None)\
        .paginate(page, per_page=20, error_out=False)
    users = pagination.items
    return render_template('role_auth/admin.html', page=page, users=users,
                           pagination=pagination)


@role_auth.route('/admin/yes_stu/<id>')
@login_required
@admin_required
def yes_stu(id):
    user = User.query.get_or_404(id)
    user.photos_uploaded = False
    user.vrole = VRole.query.filter_by(name='student').first()
    db.session.add(user)
    send_email(user.email, '身份认证审核成功', 'role_auth/email/yes_stu', user=user)
    return redirect(url_for('role_auth.admin',
                            page=request.args.get('page', 1, type=int)))


@role_auth.route('/admin/yes_teacher/<id>')
@login_required
@admin_required
def yes_tea(id):
    user = User.query.get_or_404(id)
    user.photos_uploaded = False
    user.vrole = VRole.query.filter_by(name='teacher').first()
    db.session.add(user)
    send_email(user.email, '身份认证审核成功', 'role_auth/email/yes_stu', user=user)
    return redirect(url_for('role_auth.admin',
                            page=request.args.get('page', 1, type=int)))


@role_auth.route('/admin/no/<id>')
@login_required
@admin_required
def no(id):
    user = User.query.get_or_404(id)
    user.photos_uploaded = False
    db.session.add(user)
    send_email(user.email, '身份认证审核被驳回', 'role_auth/email/no', user=user)
    return redirect(url_for('role_auth.admin',
                            page=request.args.get('page', 1, type=int)))