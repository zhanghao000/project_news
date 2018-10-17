from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis

from config import DevelopmentConfig

app = Flask(__name__)

# 加载配置
app.config.from_object(DevelopmentConfig)

# 初始化数据库对象
db = SQLAlchemy(app)

# 初始化redis对象
redis_store = StrictRedis(host=DevelopmentConfig.REDIS_HOST,
                          port=DevelopmentConfig.REDIS_PORT,
                          password=DevelopmentConfig.REDIS_PASSWORD,
                          db=DevelopmentConfig.REDIS_DB)

# 初始化Session配置
Session(app)

# 设置csrf保护
CSRFProtect(app)