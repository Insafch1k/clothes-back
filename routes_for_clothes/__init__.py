__all__ = ("clothes_blueprint",)

from flask import Blueprint
# from .routes_for_clothes import clothes_blueprint as clothes
from .add_photos import add_photos

clothes_blueprint = Blueprint("clothes_main", __name__, url_prefix='/clothes')
# clothes_blueprint.register_blueprint(clothes)
clothes_blueprint.register_blueprint(add_photos)
