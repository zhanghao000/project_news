from flask import request, jsonify, current_app, make_response

from info import redis_store, constants
from info.modules.passport import passport_blu
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET


@passport_blu.route("/image_code")
def get_image_code():
    """
    生成图片验证码并返回给浏览器
    :return:
    """
    # 1. 获取参数
    image_code_id = request.args.get("imageCodeId", None)

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
