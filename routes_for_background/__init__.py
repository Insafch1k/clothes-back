__all__ = ("background_blueprint",)

from flask import Blueprint
from .background_routes import background_blueprint as background

background_blueprint = Blueprint("background_main", __name__, url_prefix='/human')
background_blueprint.register_blueprint(background)
