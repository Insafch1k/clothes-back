__all__ = ("clothes_blueprint",)

from flask import Blueprint
from .routes_for_clothes import clothes_blueprint as clothes  # Он скоро удалится
from .add_photos import add_photos
from .recovery_photos import recovery_photos
from .clothes_fetch_routes import get_wardrobe_catalog
from .get_deleted_photos_clothes import get_deleted_clothes_photos
from .delete_photos import delete_photos
from .putting_on_clothes import putting_on_clothes
from .get_admin_clothes import get_admin_clothes

clothes_blueprint = Blueprint("clothes_main", __name__, url_prefix='/clothes')
clothes_blueprint.register_blueprint(get_wardrobe_catalog)
clothes_blueprint.register_blueprint(add_photos)
clothes_blueprint.register_blueprint(recovery_photos)
clothes_blueprint.register_blueprint(get_deleted_clothes_photos)
clothes_blueprint.register_blueprint(clothes)  # Он скоро удалится
clothes_blueprint.register_blueprint(delete_photos)
clothes_blueprint.register_blueprint(putting_on_clothes)
