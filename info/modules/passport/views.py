import random
import re
from datetime import datetime

from flask import request, jsonify, current_app, make_response, session

from info import redis_store, constants, db
from info.models import User
from info.modules.passport import passport_blu
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET


@passport_blu.route("/logout")
def logout():
    """
    退出登录, 删除session中的值
    :return: 返回退出信息
    """
    session.pop("user_id", None)
    session.pop("user_mobile", None)
    session.pop("user_nick_name", None)

    return jsonify(errno=RET.OK, errmsg="已退出")


@passport_blu.route("/login", methods=["post"])
def login():
    """
    点击登录按钮, 发起登录请求
    :return: 返回登录结果errno 和 errmsg
    """
    # 1. 获取参数
    params_dict = request.json
    if not params_dict:
        return jsonify(errno=RET.REQERR, errmsg="请求错误")
    mobile = params_dict.get("mobile")
    password = params_dict.get("password")

    # 2. 参数校验
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 3. 查询用户是否存在
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")
    if not user:
        return jsonify(errno=RET.NODATA, errmsg="用户不存在")
    # 密码校验, 调用check_password方法自动校验
    if not user.check_passowrd(password):
        return jsonify(errno=RET.PWDERR, errmsg="用户名或密码错误")

    # 4. 记录最近登录的时间, 修改数据自动commit
    user.last_login = datetime.now()

    # 5. 记录用户登录状态到session
    session["user_id"] = user.id
    session["user_mobile"] = user.mobile
    session["user_nick_name"] = user.nick_name

    # 6. 返回登录结果
    return jsonify(errno=RET.OK, errmsg="登录成功")


@passport_blu.route("/register", methods=["post"])
def register():
    """
    点击注册按钮,发起注册请求
    :return: 返回注册结果, errno 和 errmsg
    """
    # 1. 获取参数
    params_dict = request.json
    if not params_dict:
        return jsonify(errno=RET.REQERR, errmsg="请求错误")
    mobile = params_dict.get("mobile")
    sms_code = params_dict.get("smscode")
    password = params_dict.get("password")

    # 2. 参数校验
    # 非空校验
    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 手机号正则验证
    if not re.match(r"^1[3578]\d{9}$", mobile):
        return jsonify(errno=RET.DATAERR, errmsg="手机号格式不正确")

    # 3. 从redis中获取短信验证码, 进行核对
    try:
        real_sms_code = redis_store.get("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")
    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码过期")
    if real_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码输入错误")

    # 验证通过, 删除redis中的短信验证码
    try:
        redis_store.delete("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)

    # 4. 初始化user模型, 并保存到数据库中
    user = User()
    user.nick_name = mobile
    user.mobile = mobile
    # 保存密码, 自动调用propert装饰后的方法, 加密为passwor_hash
    user.password = password
    # 记录最近登录的时间
    user.last_login = datetime.now()

    # 配置teardown后自动commit属性, 操作数据库后自动commit
    db.session.add(user)

    # 5. 记录用户登录状态到session
    session["user_id"] = user.id
    session["user_mobile"] = user.mobile
    session["user_nick_name"] = user.nick_name

    # 6. 返回注册结果
    return jsonify(errno=RET.OK, errmsg="注册成功")


@passport_blu.route("/sms_code", methods=["post"])
def send_sms_code():
    """
    发送短信验证码
    :return: 返回发送结果
    """
    # 1. 获取参数
    params_dict = request.json
    if not params_dict:
        return jsonify(errno=RET.REQERR, errmsg="请求错误")
    mobile = params_dict.get("mobile")
    image_code = params_dict.get("image_code")
    image_code_id = params_dict.get("image_code_id")

    # 2. 参数校验
    # 非空校验
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 手机号正则验证
    if not re.match(r"^1[3578]\d{9}$", mobile):
        return jsonify(errno=RET.DATAERR, errmsg="手机号格式不正确")

    # 3. 从redis中取出图片验证码内容进行验证
    try:
        real_image_code = redis_store.get("ImageCodeId_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码已过期")

    if real_image_code.upper() != image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码输入错误")

    # 验证成功, 删除redis中的图片验证码内容
    try:
        redis_store.delete("ImageCodeId_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)

    # 4. 校验该手机号是否已被注册
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if user:
        return jsonify(errno=RET.DATAEXIST, errmsg="该手机号已被注册")

    # 5. 生成随机的六位数字, 发送短信验证码
    sms_code = "".join([str(random.randint(0, 9)) for i in range(6)])
    # 假装发送短信验证码
    current_app.logger.debug("短信验证码为: {}".format(sms_code))

    # 如果短信发送失败, 则返回第三方平台错误
    # 如果发送成功, 将短信验证码保存在redis中, 用于注册时验证
    try:
        redis_store.set("SMS_" + mobile, sms_code, ex=constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库错误, 数据保存失败")
    return jsonify(errno=RET.OK, errmsg="短信验证码发送成功")


@passport_blu.route("/image_code")
def get_image_code():
    """
    生成图片验证码
    :return: 返回图片验证码给浏览器
    """
    # 1. 获取参数
    url_params = request.args
    if not url_params:
        return jsonify(errno=RET.REQERR, errmsg="请求错误")
    image_code_id = url_params.get("imageCodeId", None)

    # 2. 校验参数
    if not image_code_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 3. 生成图片验证码
    name, text, image = captcha.generate_captcha()

    # 4. 保存生成的验证码内容至redis中
    try:
        redis_store.set("ImageCodeId_" + image_code_id, text, ex=constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    # 5. 返回图片验证码给浏览器,设置响应头中的数据格式
    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"
    return response
