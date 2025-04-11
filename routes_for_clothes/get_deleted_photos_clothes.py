from flask import Blueprint, jsonify
import logging
from dal.db_query import ManageQuery

get_deleted_clothes_photos = Blueprint("get_deleted_clothes_photos", __name__)


@get_deleted_clothes_photos.route("/deleted/photos/<user_name>", methods=["GET"])
def get_back_deleted_clothes_photo(user_name):
    try:
        id_user = ManageQuery.get_id_user(user_name)
        if id_user is None:
            return jsonify({"error": f"user_name '{user_name}' не найден"}), 404

        photos = ManageQuery.get_deleted_photos_by_type(id_user, "clothes")
        if not photos:
            return jsonify({
                "error": f"Удаленные фото одежды для пользователя '{user_name}' не найдены"
            }), 404

        return jsonify({
            "photo_type": "clothes",
            "user_name": user_name,
            "deleted_photos": photos
        }), 200

    except Exception as error:
        logging.exception("Ошибка при получении удалённых фото одежды")
        return jsonify({"error": f"Ошибка сервера: {str(error)}"}), 500
