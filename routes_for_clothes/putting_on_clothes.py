from flask import Blueprint, jsonify
from dal.db_query import ManageQuery
from config import PLACEHOLDER_IMAGE

putting_on_clothes = Blueprint("putting_on_clothes", __name__)


@putting_on_clothes.route("/try_on/<user_name>/<id_clothes>", methods=["GET"])
def try_on_clothes(user_name, id_clothes):
    """
    Роут-заглушка для кнопки "одеть вещь".
    Принимает параметры как настоящий роут, но возвращает фото-заглушку.
    """
    try:
        id_user = ManageQuery.get_id_user(user_name)
        if not id_user:
            return jsonify({"error": f"user_name '{user_name}' не найден"}), 404

        photo_path = ManageQuery.get_path_clothes(id_clothes)
        if not photo_path:
            return jsonify({"error": f"id_clothes '{id_clothes}' не найден"}), 404

        placeholder_image = PLACEHOLDER_IMAGE

        # Возвращаем заглушку
        return jsonify({
            "status": "success",
            "message": "Это роут-заглушка. Функционал одевания вещей пока не реализован.",
            "clothes": placeholder_image
        }), 200

    except Exception as error:
        return jsonify({"error": f"Ошибка при обработке запроса: {str(error)}"}), 500
