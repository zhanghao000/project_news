import random
import re

from flask import request, jsonify, current_app, make_response

from info import redis_store, constants
from info.models import User
from info.modules.passport import passport_blu
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET


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
