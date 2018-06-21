from . import user_blue
from flask import render_template, g, abort, redirect, url_for
from info.comment import user_model


@user_blue.route('/index')
@user_model
def index():

    user = g.user

    if not user:
        return redirect(url_for("news.index"))

    data = {
        "user": user
    }

    return render_template('html/user.html', context=data)


# 用户基本资料
@user_blue.route('/info')
@user_model
def info():

    user = g.user

    if not user:
        abort(404)

    return render_template('html/user_base_info.html')


# 头像设置
@user_blue.route('/user_pic')
@user_model
def pic():

    user = g.user

    if not user:
        abort(404)

    return render_template('html/user_pic_info.html')


# 用户关注 user_follow
@user_blue.route('/follow')
@user_model
def follow():

    user = g.user

    if not user:
        abort(404)

    return render_template('html/user_follow.html')


# 用户密码修改 user_pass_info
@user_blue.route('/pwd')
@user_model
def pwd():

    user = g.user

    if not user:
        abort(404)

    return render_template('html/user_pass_info.html')


# 用户收藏新闻列表 user_collection
@user_blue.route('/collection')
@user_model
def collection():

    user = g.user

    if not user:
        abort(404)

    return render_template('html/user_collection.html')


# 用户去发布新闻 user_news_release
@user_blue.route('/release')
@user_model
def release():

    user = g.user

    if not user:
        abort(404)

    return render_template('html/user_news_release.html')


# 用户发布的新闻列表 user_news_list
@user_blue.route('/release_news')
@user_model
def release_news():

    user = g.user

    if not user:
        abort(404)

    return render_template('html/user_news_list.html')
