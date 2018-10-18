from flask import Blueprint


passport_blu = Blueprint("passport_blu", __name__)

from . import views