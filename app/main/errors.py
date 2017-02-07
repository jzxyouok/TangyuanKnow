from . import main
from flask_wtf.csrf import CSRFError
from flask import redirect, url_for


@main.app_errorhandler(404)
def page_not_found(e):
    return 'Page not found', 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return 'Internal server error', 500


@main.app_errorhandler(CSRFError)
def csrf_error(e):
    return redirect(url_for('auth.login'))
