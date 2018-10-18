from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from info import db, create_app, models

app = create_app("development")

# 集成flask_script
manager = Manager(app)

# 集成数据库迁移扩展
Migrate(app, db)
manager.add_command("db", MigrateCommand)

if __name__ == '__main__':
    manager.run()
