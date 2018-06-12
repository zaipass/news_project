from flask import session, current_app, g
from info.utils import models


# 闭包 --> 装饰器

def user_model(func):
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
