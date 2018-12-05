from flask import Flask
from config import configs
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect, csrf
from logging.handlers import RotatingFileHandler
import logging

from pymysql import install_as_MySQLdb

install_as_MySQLdb()


db = SQLAlchemy()
redis_store = None


def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(configs[config_name])

    db.init_app(app)

    global redis_store

    redis_store = StrictRedis(configs[config_name].REDIS_HOST, configs[config_name].REDIS_PORT)

    Session(app)

    CSRFProtect(app)

    # 生成 CSRF_token
    @app.after_request
    def after_request(response):
        csrf_token = csrf.generate_csrf()
        response.set_cookie("csrf_token", csrf_token)
        return response

    from info.news import news_blue
    app.register_blueprint(news_blue)
    from info.passport import passport_blue
    app.register_blueprint(passport_blue)
    from info.user import user_blue
    app.register_blueprint(user_blue)

    # 开启日志
    create_log(config_name)

    # 添加过滤器
    from info.comment import rank
    app.add_template_filter(rank)

    return app


def create_log(config_name):
    logging.basicConfig(level=configs[config_name].LOGGING_DEBUG)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)

