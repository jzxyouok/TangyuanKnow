from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_pagedown import PageDown
from flask_wtf.csrf import CSRFProtect
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_qiniustorage import Qiniu


db = SQLAlchemy()
bootstrap = Bootstrap()
moment = Moment()
mail = Mail()
pagedown = PageDown()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
photos = UploadSet('photos', IMAGES)
qiniu_store = Qiniu()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    pagedown.init_app(app)
    csrf.init_app(app)
    qiniu_store.init_app(app)

    # upload stuff
    configure_uploads(app, photos)
    patch_request_class(app, size=app.config.get('MAX_CONTENT_LENGTH'))

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # from .meetbot import meetbot as meetbot_blueprint
    # app.register_blueprint(meetbot_blueprint, url_prefix='/meetbot')

    from .role_auth import role_auth as role_auth_blueprint
    app.register_blueprint(role_auth_blueprint, url_prefix='/role-auth')

    return app
