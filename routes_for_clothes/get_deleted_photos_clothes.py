from flask import Blueprint, jsonify
import logging
from dal.db_query import ManageQuery
import base64

get_deleted_clothes_photos = Blueprint("get_deleted_clothes_photos", __name__)


@get_deleted_clothes_photos.route("/deleted/photos/<user_name>", methods=["GET"])
def get_back_deleted_clothes_photo(user_name):
    try:
        id_user = ManageQuery.get_id_user(user_name)
        if id_user is None:
            return jsonify({"error": f"user_name '{user_name}' not found"}), 404

        photos = ManageQuery.get_deleted_photos_by_type(id_user, "clothes")
        if not photos:
            return jsonify({
                "error": f"Deleted photos of clothes '{user_name}' not found"
            }), 404

        # Encode each photo in base64
        encoded_photos = []
        for photo in photos:
            try:
                with open(photo["photo_path"], "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    encoded_photos.append({
                        "id_photo": photo["id_photo"],
                        "photo_base64": encoded_string
                    })
            except Exception as e:
                logging.error(f"Error encoding photo {photo['photo_path']}: {str(e)}")
                continue

        if not encoded_photos:
            return jsonify({
                "error": f"Failed to encode deleted photos for user '{user_name}'"
            }), 500

        return jsonify({
            "photo_type": "clothes",
            "user_name": user_name,
            "deleted_photos": encoded_photos
        }), 200

    except Exception as error:
        logging.exception("Ошибка при получении удалённых фото одежды")
        return jsonify({"error": f"Ошибка сервера: {str(error)}"}), 500
