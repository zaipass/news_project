from . import news_blue
from flask import render_template, session, g, request, current_app, abort, jsonify
from info.comment import user_model
from info.utils import models
from info.utils import constants
from info.utils.response_code import RET
from info import db
import datetime


# 评论
@news_blue.route("/comments", methods=["POST"])
@user_model
def comments():
    # 评论有有两种form表单框 1. 用户评论新闻 2. 用户评论用户
    # 需要: 新闻id 用户id 表单内容 父id

    user = g.user

    news_id = request.json.get("news_id")

    content = request.json.get("content")

    parent_id = request.json.get("parent_id")

    if not news_id:
        return jsonify(errno=RET.NODATA, errmsg="新闻不存在")

    if not content:
        return jsonify(errno=RET.NODATA, errmsg="请输入内容")

    if not user:
        return jsonify(errno=RET.NODATA, errmsg="用户不存在")

    # 保存评论 (评论新闻)
    comment = models.Comment()
    comment.content = content
    comment.user_id = user.id
    comment.news_id = news_id
    comment.create_time = datetime.datetime.now()

    if parent_id:
        comment.parent_id = parent_id

    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据无法保存")

    print(comment)

    params = {
        "user": user.to_dict(),
        "comment": comment.to_dict()
    }

    return jsonify(errno=RET.OK, errmsg="评论成功", data=params)


# 新闻收藏
@news_blue.route("/collection", methods=["GET"])
@user_model
def collection():
    user = g.user

    if not user:
        return jsonify(errno=RET.NODATA, errmsg="用户未登录")

    action = request.args.get("action")

    cur_news_id = request.args.get("news_id")

    if not all([action, cur_news_id]):
        return jsonify(errno=RET.NODATA, errmsg="参数不完整")

    # 查看是否已经进行收藏
    try:
        news_collected = user.collection_news.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询信息错误")

    news_id_list = [news.id for news in news_collected]

    print(news_id_list, cur_news_id)

    if action not in ["collection", "collected"]:
        return jsonify(errno=RET.DATAERR, errmsg="类型错误")

    news = models.News.query.get(cur_news_id)

    if action == "collection":  # 进行收藏
        # 多对多的收藏
        user.collection_news.append(news)
        msg = "收藏成功"
    else:
        user.collection_news.remove(news)
        msg = "取消成功"

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库操作错误")

    return jsonify(errno=RET.OK, errmsg=msg)


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

    is_collected = False

    if user:
        # 优化收藏, 判断当前用户是否收藏了此新闻
        try:
            news_collected = user.collection_news.all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库查询信息错误")

        news_id_list = [news.id for news in news_collected]

        print(num_id, news_id_list)

        if num_id in news_id_list:
            is_collected = True

    # 显示评论
    try:
        news_comments = models.Comment.query.order_by(models.Comment.create_time.desc()).\
            filter(models.Comment.news_id == num_id).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询信息错误")

    news_comments = [comments_object.to_dict() for comments_object in news_comments]

    context = {
        "user": user,
        "news": news_list,
        "detail_news": news.to_dict(),
        "is_collected": is_collected,
        "news_comments": news_comments
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
