# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from flask import redirect, session, url_for, render_template, flash, abort, request, current_app, jsonify

from . import main, forms
from .. import db
from ..models import User, Permission, Role, Answer, Question, Vote
from ..decorators import permission_required, admin_required
from flask_login import login_required, current_user
from .forms import EditProfileForm, EditProfileAdminForm


@main.route('/', methods=['POST', 'GET'])
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Answer.query.order_by(Answer.timestamp.desc()).paginate(page, per_page=50, error_out=False)
    qas = [{'question': Question.query.filter_by(id=item.belong).first(),
            'answer': item,
            'answerer': User.query.filter_by(id=item.answerer_id).first()}
           for item in pagination.items]
    return render_template('index.html', page=page, qas=qas, pagination=pagination)


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


@main.route('/vote-post', methods=['POST'])
# @login_required
def vote_post():
    # 如果用户未登录，返回相关信息给AJAX，手动处理重定向。
    # 如果交给@login_required自动重定向的话，
    # AJAX不能正确处理这个重定向
    if not current_user.is_authenticated:
        return jsonify({
            'status': 302,
            'location': url_for(
                'auth.login',
                next=request.referrer.replace(
                    url_for('.index', _external=True)[:-1], ''))
        })
    # 以post方式传的数据在存储在的request.form中，以get方式传输的在request.args中~~
    answer = Answer.query.get_or_404(int(request.form.get('id')))
    if current_user.id == answer.answerer_id:
        return 'disable'
    if current_user.vote_answer(answer):
        return 'vote'
    else:
        return 'cancel'
