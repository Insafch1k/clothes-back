__all__ = ("users_blueprint",)

from flask import Blueprint
from .routes_for_users import routes_for_users

users_blueprint = Blueprint("users_main", __name__, url_prefix='/users')
users_blueprint.register_blueprint(routes_for_users)
