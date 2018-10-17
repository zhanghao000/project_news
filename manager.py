from flask import Flask, session
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis


class Config(object):
    """项目基本配置"""
    # 开启调试模式
    DEBUG = True

    SECRET_KEY = "M+HsMyDEAQnFABFN0/tVEq/PhvyB6TAltR88pWdx9G1k66D3DDcASv0pMfJ1GHC4"

    # mysql数据库连接配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:123456@127.0.0.1:3306/project_news"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # redis连接配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    REDIS_PASSWORD = "123456"
    REDIS_DB = 1

    # Session相关配置
    # 配置session存储在redis
    SESSION_TYPE = "redis"
    # 设置session会过期, 设置过期时间
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = 86400 * 2
    # 设置cookie中的session_id被加密签名处理
    SESSION_USE_SIGNER = True
    # 保存session的redis连接配置
    SESSION_REDIS = StrictRedis(host=REDIS_HOST,
                                port=REDIS_PORT,
                                password=REDIS_PASSWORD,
                                db=REDIS_DB)


app = Flask(__name__)

# 加载配置
app.config.from_object(Config)

# 初始化数据库对象
db = SQLAlchemy(app)

# 初始化redis对象
redis_store = StrictRedis(host=Config.REDIS_HOST,
                          port=Config.REDIS_PORT,
                          password=Config.REDIS_PASSWORD,
                          db=Config.REDIS_DB)

# 初始化Session配置
Session(app)

# 设置csrf保护
CSRFProtect(app)

# 集成flask_script
manager = Manager(app)

# 集成数据库迁移扩展
Migrate(app, db)
manager.add_command("db", MigrateCommand)


@app.route("/")
def index():
    session["name"] = "laowang"
    return "index"


if __name__ == '__main__':
    manager.run()
