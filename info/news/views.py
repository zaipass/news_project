from . import news_blue
from flask import render_template, session, g, request, current_app, abort, jsonify
from info.comment import user_model
from info.utils import models
from info.utils import constants
from info.utils.response_code import RET


@news_blue.route("/news_all", methods=["GET"])
def news_all():
    paginate = None
    # 当前种类
    current_id = request.args.get("cid", 1)
    # 当前页
    cur_page = request.args.get("page", 1)

    print(current_id, cur_page)

    if not all([current_id, cur_page]):
        abort(404)

    try:
        current_id = int(current_id)
        cur_page = int(cur_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="数据转化失败")

    try:
        if current_id == 1:
            paginate = models.News.query.\
                paginate(cur_page, constants.HOME_PAGE_MAX_NEWS, False)
            print(paginate)
        else:
            paginate = models.News.query.filter(models.News.category_id == current_id). \
                paginate(cur_page, constants.HOME_PAGE_MAX_NEWS, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")

    objects_news = paginate.items
    total_page = paginate.pages
    current_page = paginate.page

    news_list = []

    for news in objects_news:
        news_list.append(news.to_dict())

    context = {
        "news": news_list,
        "tpage": total_page,
        "cpage": current_page
    }

    return jsonify(errno=RET.OK, context=context, errmsg="成功")


@news_blue.route("/index")
@user_model
def index():

    user = g.user

    context = {
        "user": user if user else None
    }

    return render_template("index.html", context=context)