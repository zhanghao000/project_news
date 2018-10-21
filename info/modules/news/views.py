from flask import render_template, current_app, session, request, jsonify

from info import constants
from info.models import User, News, Category
from info.modules.news import index_blu
from info.utils.response_code import RET


@index_blu.route("/news_list")
def get_news_list():
    """
    首页主体新闻数据的显示
    :return: 返回查询结果和具体新闻数据
    """
    # 1. 获取参数
    cid = request.args.get("cid", "1")
    page = request.args.get("page", "1")
    per_page = request.args.get("per_page", constants.HOME_PAGE_MAX_NEWS)

    # 2. 校验参数
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 3. 查询新闻相关数据
    filters = []
    if cid != 1:
        filters.append(News.category_id == cid)
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")
    page = paginate.page
    total_page = paginate.pages
    news_list = paginate.items
    # 将查询对象转化为数据
    news_list = [news.to_basic_dict() for news in news_list]

    # 4. 返回数据
    data = {
        "cid": cid,
        "page": page,
        "total_page": total_page,
        "news_list": news_list
    }
    return jsonify(errno=RET.OK, errmsg="ok", data=data)


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
    # 将查询对象转化为数据
    user_info = user.to_dict() if user else None

    # 查询首页右侧的点击排行新闻数据并返回
    news_list = list()
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger(e)
    if not news_list:
        # 将查询对象转化为数据
        news_list = [news.to_basic_dict() for news in news_list]

    # 查询首页新闻分类数据并返回
    category_list = []
    try:
        category_list = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
    if not category_list:
        # 将查询对象转化为数据
        category_list = [category.to_dict() for category in category_list]

    data = {
        "user_info": user_info,
        "news_list": news_list,
        "category_list": category_list
    }
    return render_template("news/index.html", data=data)


@index_blu.route("/favicon.ico")
def favicon():
    return current_app.send_static_file("news/favicon.ico")
