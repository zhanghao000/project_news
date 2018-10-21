from flask import render_template, current_app, session

from info import constants
from info.models import User, News
from info.modules.news import index_blu


@index_blu.route("/")
def index():
    """
    首页相关数据显示
    :return: 返回渲染后的首页页面
    """

    # 从session中获取当前用户的登录状态
    user_id = session.get("user_id")
    user = None
    if user_id:
        try:
            user = User.query.filter().get(user_id)
        except Exception as e:
            current_app.logger.error(e)
    user_info = user.to_dict() if user else None

    # 查询首页右侧的点击排行新闻数据并返回
    news_list = list()
    try:
        news_list = News.query.order_by(News.create_time.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger(e)
    news_list = [news.to_basic_dict() for news in news_list]

    data = {
        "user_info": user_info,
        "news_list": news_list
    }
    return render_template("news/index.html", data=data)


@index_blu.route("/favicon.ico")
def favicon():
    return current_app.send_static_file("news/favicon.ico")
