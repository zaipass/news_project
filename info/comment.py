from flask import session, current_app, g
from info.utils import models
from functools import wraps


# 过滤器
def rank(num):
    if num == 1:
        return "first"
    elif num == 2:
        return "second"
    elif num == 3:
        return "third"
    else:
        return ""


# 闭包 --> 装饰器

def user_model(func):
    # View function mapping is overwriting an existing endpoint function: news.inner
    @wraps(func)
    def inner(*args, **kwargs):
        user = None
        uid = session.get("uid")

        try:
            if uid:
                user = models.User.query.get(uid)
        except Exception as e:
            current_app.logger.error(e)

        g.user = user

        return func(*args, **kwargs)
    return inner
