# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or '2B|!2B, there is a question'

    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # Email stuff
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'your email addr'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'your email passwd'
    # 邮箱密码是QQ邮箱的授权码, 需要在QQ邮箱单独申请

    # administrator's email account
    TYKNOW_MAIL_SUBJECT_PREFIX = '[唐院知乎]'
    TYKNOW_MAIL_SENDER = MAIL_USERNAME + '@qq.com'
    TYKNOW_ADMIN = os.environ.get('TYKNOW_ADMIN') or 'your administrator email account'

    # Upload stuff
    UPLOADED_PHOTOS_DEST = os.getcwd() + '/photos'
    MAX_CONTENT_LENGTH = 300 * 1024

    # 七牛云
    QINIU_ACCESS_KEY = os.environ.get('QINIU_ACCESS_KEY') or 'access key'
    QINIU_SECRET_KEY = os.environ.get('QINIU_SECRET_KEY') or 'secret key'
    QINIU_BUCKET_NAME = os.environ.get('QINIU_BUCKET_NAME') or 'bucket name'
    QINIU_BUCKET_DOMAIN = os.environ.get('QINIU_BUCKET_DOMAIN') or 'bucket domain'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'date-dev.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI') or \
                              'mysql+pymysql://username:password@url:port/datebase'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}