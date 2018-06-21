from flask import Blueprint

user_blue = Blueprint('users', __name__, url_prefix='/users')

from . import views
