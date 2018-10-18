from info import redis_store
from info.modules.news import index_blu


@index_blu.route("/")
def index():
    print(redis_store.get("name"))

    return "index"