import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis

from config import config

# 初始化数据库对象
db = SQLAlchemy()
redis_store = None  # type: StrictRedis


def setup_log(config_name):
    """项目日志的设置"""
    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    """工厂方法创建实例应用app, 通过传入参数设定不同配置"""
    # 项目日志创建
    setup_log(config_name)

    # 创建flask本地应用
    app = Flask(__name__)

    # 加载配置
    app.config.from_object(config[config_name])

    # 手动执行app对db的初始化
    db.init_app(app)

    # 初始化redis对象
    global redis_store
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST,
                              port=config[config_name].REDIS_PORT,
                              password=config[config_name].REDIS_PASSWORD,
                              db=config[config_name].REDIS_DB,
                              decode_responses=True)

    # 初始化Session配置
    Session(app)

    # 设置csrf保护
    CSRFProtect(app)

    # 注册首页蓝图
    from info.modules.news import index_blu
    app.register_blueprint(index_blu)
    # 注册passport蓝图
    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)

    return app
