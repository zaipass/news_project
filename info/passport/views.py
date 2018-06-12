from . import passport_blue
from info.utils.captcha.captcha import captcha
from flask import request, jsonify, abort, make_response, current_app
from info import redis_store


# 获取图片验证码
@passport_blue.route("/image_code")
def image_code():
    # 获取图片 GET 方法
    if request.method == 'GET':

        uuid = request.args.get('imageCodeId')

        if not uuid:
            abort(404)

        # 返回三个数据
        image_id, code, image_bin = captcha.generate_captcha()

        if not all([image_id, code, image_bin]):
            abort(404)

        # 保存code 到Redis数据库
        try:
            redis_store.set("imageCode:"+uuid, code)
        except Exception as e:
            current_app.logger.error(e)
            abort(400)

        response = make_response(image_bin)

        response.headers["Content-Type"] = "image/png"

        return response
