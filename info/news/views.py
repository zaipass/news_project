from . import news_blue
from flask import render_template


@news_blue.route("/index")
def index():
    return render_template("index.html")