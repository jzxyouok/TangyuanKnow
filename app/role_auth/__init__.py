from flask import Blueprint

role_auth = Blueprint('role_auth', __name__)

from . import views