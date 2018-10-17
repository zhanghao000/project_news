from flask import Flask, session
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis

from config import Config

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
