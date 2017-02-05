# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from flask import redirect, session, url_for, render_template, flash, abort, request, current_app

from . import main, forms
from .. import db
from ..models import User, Permission, Role
from ..decorators import permission_required, admin_required
from flask_login import login_required, current_user
from .forms import EditProfileForm, EditProfileAdminForm


@main.route('/', methods=['POST', 'GET'])
def index():
    # page = request.args.get('page', 1, type=int)
    # pagination = User.query.order_by(User.score.desc()).paginate(page, per_page=50, error_out=False)
    # users = pagination.items
    return render_template('index.html', )


@main.route('/user/<nickname>')
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('个人信息已更新。')
        return redirect(url_for('.user', nickname=current_user.nickname))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.nickname = form.nickname.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('信息已更新')
        return redirect(url_for('.user', nickname=user.nickname))
    form.email.data = user.email
    form.nickname.data = user.nickname
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)
