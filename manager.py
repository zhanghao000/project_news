from flask import session
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

# 集成flask_script
from info import app, db

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
