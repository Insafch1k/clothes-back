__all__ = ("background_blueprint",)

from flask import Blueprint
from .background_routes import background_blueprint as background
from .recovery_photos import recovery_photos
from .delete_photos import delete_photos
from .add_photos import add_photos
from .background_fetch_routes import get_user_photos

background_blueprint = Blueprint("background_main", __name__, url_prefix='/human')
background_blueprint.register_blueprint(background)
background_blueprint.register_blueprint(recovery_photos)
background_blueprint.register_blueprint(delete_photos)
background_blueprint.register_blueprint(add_photos)
background_blueprint.register_blueprint(get_user_photos)
