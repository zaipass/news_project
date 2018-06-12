from . import passport_blue
from info.utils.captcha.captcha import captcha
from flask import request, jsonify, abort, make_response, current_app, session
from info import redis_store
from info.utils.response_code import RET
from info.utils.yuntongxun import sms
from info.utils import constants, models
import random
import re
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from info import db


@passport_blue.route("/logout")
def logout():
    session.pop("uid")

    if session.get("uid"):
        return jsonify(errno=RET.PARAMERR, errmsg="退出失败")

    return jsonify(errno=RET.OK, errmsg="退出")


# 登录
@passport_blue.route("/login", methods=["POST"])
def login():
    # 手机号 密码
    mobile = request.json.get("mobile")

    pwd = request.json.get("password")

    if not all([mobile, pwd]):
        return jsonify(errno=RET.NODATA, errmsg="信息填写不完整")

    # 匹配手机号
    if not re.match(r"^1[356789]\d{9}$", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号填写不正确")

    try:
        user = models.User.query.filter(models.User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="用户信息查询不到")

    if not user:
        return jsonify(errno=RET.NODATA, errmsg="该用户不存在")

    # 比较密码 -- 返回 true 或 false
    result = check_password_hash(user.password_hash, pwd)

    if not result:
        return jsonify(errno=RET.PARAMERR, errmsg="手机号或者密码错误")

    session["uid"] = user.id

    return jsonify(errno=RET.OK, errmsg="登录成功")


# 注册
@passport_blue.route("/register", methods=["POST"])
def register():
    if request.method == "POST":
        # 得到 手机号 短信验证码 密码
        mobile = request.json.get("mobile")

        sms_num = request.json.get("smscode")

        pwd = request.json.get("password")

        if not all([mobile, sms_num, pwd]):
            return jsonify(errno=RET.NODATA, errmsg="信息填写不完整")

        # 匹配手机号
        if not re.match(r"^1[356789]\d{9}$", mobile):
            return jsonify(errno=RET.PARAMERR, errmsg="手机号填写不正确")

        # 验证短信验证码
        try:
            code = redis_store.get("smsCode:"+mobile)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="无法获取数据")

        if not code:
            return jsonify(errno=RET.NODATA, errmsg="短信验证码失效")

        if code.decode() != sms_num:
            return jsonify(errno=RET.PARAMERR, errmsg="短信验证码填写不正确")

        # 密码加密
        password_hs = generate_password_hash(pwd)

        user = models.User()
        user.nick_name = mobile
        user.create_time = datetime.datetime.now()
        user.password_hash = password_hs
        user.mobile = mobile

        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="用户注册失败")

        return jsonify(errno=RET.OK, errmsg="用户注册成功")


# 短信验证码生成
@passport_blue.route("/sms_code", methods=["POST"])
def sms_code():

    if request.method == "POST":
        # 得到 手机号 图片验证码和UUID 短信验证码的生成和保存
        mobile = request.json.get("mobile")

        pic_code = request.json.get("image_code")

        uuid = request.json.get("image_code_id")

        if not all([mobile, pic_code, uuid]):
            return jsonify(errno=RET.NODATA, errmsg="信息填写不完整")

        # 匹配手机号
        if not re.match(r"^1[356789]\d{9}$", mobile):
            return jsonify(errno=RET.PARAMERR, errmsg="手机号填写不正确")

        try:
            code = redis_store.get("imageCode:"+uuid)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="服务器无法获取数据")

        if not code:
            return jsonify(errno=RET.NODATA, errmsg="图片验证码失效")

        print(code, pic_code)

        if code.decode().lower() != pic_code.lower():
            return jsonify(errno=RET.DATAERR, errmsg="图片验证码填写错误")

        # 生成短信验证码
        num = random.randint(1, 999999)

        random_num = "%06d" % num

        print(random_num)  # 生成随机数,发送用户

        # result = sms.CCP().send_template_sms(mobile, [random_num, constants.SMS_CODE_REDIS_EXPIRES/60], 1)
        #
        # if result != 0:
        #     return jsonify(errno=RET.PARAMERR, errmsg="短信验证无法发送")

        # 验证码保存Redis数据库 -- 注意时间长
        try:
            redis_store.set("smsCode:"+mobile, random_num, constants.SMS_CODE_REDIS_EXPIRES)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="短信验证码无法保存")

        return jsonify(errno=RET.OK, errmsg="发送验证码成功")


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
