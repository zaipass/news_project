from . import news_blue
from flask import render_template, session, g, request, current_app, abort, jsonify
from info.comment import user_model
from info.utils import models
from info.utils import constants
from info.utils.response_code import RET


# TODO 新闻详情页的收藏/评论


# 实现新闻详情页的显示
@news_blue.route("/detail/<int:num_id>", methods=["GET"])
@user_model
def detail(num_id):
    user = g.user

    # 根据id 查询新闻详情
    try:
        news = models.News.query.get(num_id)
        # 点击排行的查询
        news_list = models.News.query.order_by(models.News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="新闻查询错误")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻不存在")

    context = {
        "user": user,
        "news": news_list,
        "detail_news": news.to_dict()
    }

    return render_template("html/detail.html", context=context)


# 首页显示新闻, 实现滑动翻页
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
            paginate = models.News.query.order_by(models.News.create_time.desc()).\
                paginate(cur_page, constants.HOME_PAGE_MAX_NEWS, False)
            print(paginate)
        else:
            paginate = models.News.query.filter(models.News.category_id == current_id)\
                .order_by(models.News.create_time.desc()). \
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


@news_blue.route("/")
@user_model
def index():

    user = g.user

    # 根据click 进行排序
    try:
        news_list = models.News.query.order_by(models.News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    context = {
        "user": user if user else None,
        "news": news_list
    }

    return render_template("index.html", context=context)
