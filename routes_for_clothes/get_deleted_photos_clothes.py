from flask import Blueprint, jsonify, request
import logging
from dal.db_query import ManageQuery
from bl.utils.base64_utils import Base64Utils

get_deleted_clothes_photos = Blueprint("get_deleted_clothes_photos", __name__)


@get_deleted_clothes_photos.route("/deleted/photos/<user_name>", methods=["GET"])
def get_back_deleted_clothes_photo(user_name):
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=20, type=int)

    if page < 1 or limit < 1:
        return jsonify({"error": "page and limit must be >= 1"}), 400

    try:
        id_user = ManageQuery.get_id_user(user_name)
        if id_user is None:
            return jsonify({"error": f"user_name '{user_name}' not found"}), 404

        photos = ManageQuery.get_deleted_photos_by_type(id_user, "clothes", page, limit)
        if not photos:
            return jsonify({
                "error": f"Deleted photos of clothes '{user_name}' not found"
            }), 404

        photo_list = [
            {
                "id_photo": photo["id_photo"],
                "photo": Base64Utils.encode_to_base64(photo["photo_path"])
            }
            for photo in photos
        ]

        if not photo_list:
            return jsonify({
                "error": f"Failed to encode deleted photos for user '{user_name}'"
            }), 500

        return jsonify({
            "photo_type": "clothes",
            "user_name": user_name,
            "limit": page,
            "offset": limit,
            "deleted_photos": photo_list
        }), 200

    except Exception as error:
        logging.exception("Ошибка при получении удалённых фото одежды")
        return jsonify({"error": f"Ошибка сервера: {str(error)}"}), 500
