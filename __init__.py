__all__ = ("all_blueprints",)
from flask import Blueprint
from routes_for_clothes import clothes_blueprint
from routes_for_background import background_blueprint

all_blueprints = Blueprint("all_routes", __name__)
all_blueprints.register_blueprint(clothes_blueprint)
all_blueprints.register_blueprint(background_blueprint)
