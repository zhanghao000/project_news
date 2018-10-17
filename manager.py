import logging

from flask import current_app
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from info import db, create_app

app = create_app("development")

# 集成flask_script
manager = Manager(app)

# 集成数据库迁移扩展
Migrate(app, db)
manager.add_command("db", MigrateCommand)


@app.route("/")
def index():

    logging.debug("调试信息")
    logging.error("错误信息")

    current_app.logger.debug("调试信息")

    return "index"


if __name__ == '__main__':
    manager.run()
