from flask import render_template, current_app, session

from info.models import User
from info.modules.news import index_blu


@index_blu.route("/")
def index():
    """
    首页相关数据显示
    :return: 返回渲染后的首页页面
    """

    # 从session中获取当前用户的登录状态
    user_id = session["user_id"]
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
    user_info = user.to_dict() if user else None
    data = {
        "user_info": user_info
    }

    return render_template("news/index.html", data=data)


@index_blu.route("/favicon.ico")
def favicon():
    return current_app.send_static_file("news/favicon.ico")
