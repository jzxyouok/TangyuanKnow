# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'ajsbdfkbk23briupHP*(T(*Yiug3br'  # 此处需要脸滚键盘
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or '1'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or '1'

    TYKNOW_MAIL_SUBJECT_PREFIX = '[唐院知乎]'
    TYKNOW_MAIL_SENDER = MAIL_USERNAME + '@qq.com'
    TYKNOW_ADMIN = os.environ.get('TYKNOW_ADMIN') or '1' # 修改为你自己的

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