from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis

from config import config

# 初始化数据库对象
db = SQLAlchemy()


def create_app(config_name):
    """工厂方法创建实例应用app, 通过传入参数设定不同配置"""
    app = Flask(__name__)

    # 加载配置
    app.config.from_object(config[config_name])

    # 手动执行app对db的初始化
    db.init_app(app)

    # 初始化redis对象
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST,
                              port=config[config_name].REDIS_PORT,
                              password=config[config_name].REDIS_PASSWORD,
                              db=config[config_name].REDIS_DB)

    # 初始化Session配置
    Session(app)

    # 设置csrf保护
    CSRFProtect(app)
    return app
