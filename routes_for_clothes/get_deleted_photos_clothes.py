from flask import Blueprint, jsonify, request
import logging
from dal.db_query import ManageQuery
from bl.utils.base64_utils import Base64Utils
from flask_jwt_extended import jwt_required, get_jwt_identity

get_deleted_clothes_photos = Blueprint("get_deleted_clothes_photos", __name__)


@get_deleted_clothes_photos.route("/deleted/photos", methods=["GET"])
@jwt_required()
def get_back_deleted_clothes_photo():
    """
    Возвращает список удаленных фото одежды текущего пользователя
    """
    try:
        current_id_user = get_jwt_identity()

        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=20, type=int)

        if page < 1 or limit < 1:
            return jsonify({"error": "page and limit must be >= 1"}), 400

        offset = (page - 1) * limit  # Вычисляем правильный offset
        photos = ManageQuery.get_deleted_photos_by_type(current_id_user, "clothes", limit, offset)

        if photos is None:  # Изменим проверку на None
            return jsonify({
                "error": "Error while retrieving deleted photos"
            }), 500

        if not photos:  # Пустой список
            return jsonify({
                "error": "No deleted photos found"
            }), 404

        photo_list = [
            {
                "id_photo": photo["id_photo"],
                "photo": Base64Utils.encode_to_base64(photo["photo_path"])
            }
            for photo in photos
        ]

        return jsonify({
            "photo_type": "clothes",
            "page": page,
            "limit": limit,
            "deleted_photos": photo_list
        }), 200

    except Exception as error:
        logging.exception("Error retrieving deleted clothing photos")
        return jsonify({"error": f"Server error: {str(error)}"}), 500
