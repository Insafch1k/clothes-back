__all__ = ("auth_blueprint",)

from flask import Blueprint
from .auth import auth_blueprint as auth

auth_blueprint = Blueprint("auth_main", __name__, url_prefix='/auth')

auth_blueprint.register_blueprint(auth)
