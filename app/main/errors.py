from . import main
from flask_wtf.csrf import CSRFError
from flask import redirect, url_for, render_template


@main.app_errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@main.app_errorhandler(CSRFError)
def csrf_error(e):
    return redirect(url_for('auth.login'))
