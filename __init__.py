from flask import Blueprint

# Инициализация основного Blueprint
main_blueprint = Blueprint('main', __name__)

# Импорт и регистрация дочерних Blueprints
from routes_for_clothes import clothes_blueprint
from routes_for_background import background_blueprint

main_blueprint.register_blueprint(clothes_blueprint)
main_blueprint.register_blueprint(background_blueprint)

__all__ = ('main_blueprint',)