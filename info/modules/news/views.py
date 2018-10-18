from flask import render_template, current_app

from info import redis_store
from info.modules.news import index_blu


@index_blu.route("/")
def index():
    print(redis_store.get("name"))

    return render_template("news/index.html")


@index_blu.route("/favicon.ico")
def favicon():
    return current_app.send_static_file("news/favicon.ico")
