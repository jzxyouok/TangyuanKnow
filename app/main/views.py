# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from flask import redirect, session, url_for, render_template, flash, abort, request, current_app, jsonify

from . import main, forms
from .. import db, csrf
from ..models import User, Permission, Role, Answer, Question, Vote
from ..decorators import permission_required, admin_required
from flask_login import login_required, current_user
from .forms import EditProfileForm, EditProfileAdminForm, QuestionForm, AnswerForm
from flask_wtf.csrf import validate_csrf, ValidationError


@main.route('/', methods=['POST', 'GET'])
def index():
    form = QuestionForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
        form.validate_on_submit():
        question = Question(author=current_user._get_current_object(),
                            body=form.body.data,
                            title=form.title.data)
        db.session.add(question)
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = Answer.query.order_by(Answer.timestamp.desc()).paginate(page, per_page=50, error_out=False)
    answers = pagination.items
    return render_template('index.html',form=form, page=page, answers=answers, pagination=pagination)


@main.route('/question/<int:id>', methods=['POST', 'GET'])
def question(id):
    form = AnswerForm()
    if form.validate_on_submit():
        answer = Answer(body=form.body.data, belong=id, answerer_id=current_user.id)
        db.session.add(answer)
        redirect(url_for('main.question', id=id))
    the_question = Question.query.get_or_404(id)
    answers = the_question.answers.all()
    return render_template('question.html', question=the_question, answers=answers, form=form)


@main.route('/user/<nickname>')
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        abort(404)

    return render_template('user.html', user=user)


@main.route('/follow/<nickname>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('不存在的用户！')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('你已关注此用户！')
        redirect(url_for('.user', nickname=nickname))
    current_user.follow(user)
    flash('已关注 %s' % nickname)
    return redirect(url_for('.user', nickname=nickname))


@main.route('/unfollow/<nickname>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('该用户不存在')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('你尚未关注此用户.')
        return redirect(url_for('.user', nickname=nickname))
    current_user.unfollow(user)
    flash('你已不再关注 %s.' % nickname)
    return redirect(url_for('.user', nickname=nickname))


@main.route('/followers/<nickname>')
@login_required
def followers(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('不存在此用户')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page, per_page=20, error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title='关注了',
                           endpoint='.followers', pagination=pagination,follows=follows)


@main.route('/followed-by/<nickname>')
@login_required
def followed_by(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('不存在此用户')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=20,
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title='被关注',
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


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
@csrf.exempt
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
    # 同理，csrf token认证也要手动解决重定向
    try:
        validate_csrf(request.headers.get('X-CSRFToken'))
    except ValidationError:
        return jsonify({
            'status': 400,
            'location': url_for(
                'auth.login',
                next=request.referrer.replace(
                    url_for('.index', _external=True)[:-1], ''))
        })
    answer = Answer.query.get_or_404(int(request.form.get('id')))
    if current_user.id == answer.answerer_id:
        return 'disable'
    if current_user.vote_answer(answer):
        return 'vote'
    else:
        return 'cancel'
