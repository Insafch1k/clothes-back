from flask import Blueprint, jsonify, request
import logging
import base64
from dal.db_query import ManageQuery

get_deleted_human_photos = Blueprint("get_deleted_human_photos", __name__)


@get_deleted_human_photos.route("/deleted/photos/<user_name>", methods=["GET"])
def get_back_deleted_human_photo(user_name):
    try:
        limit = request.args.get('limit', default=20, type=int)
        offset = request.args.get('offset', default=0, type=int)

        id_user = ManageQuery.get_id_user(user_name)
        if id_user is None:
            return jsonify({"error": f"user_name  '{user_name}' not found"}), 404

        photos = ManageQuery.get_deleted_photos_by_type(id_user, "users", limit, offset)
        if not photos:
            return jsonify({
                "error": f"Deleted photos for user '{user_name}' not found"
            }), 404

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
            "photo_type": "users",
            "user_name": user_name,
            "limit": limit,
            "offset": offset,
            "deleted_photos": encoded_photos
        }), 200

    except Exception as error:
        logging.exception("Error getting deleted user photos")
        return jsonify({"error": f"Server error: {str(error)}"}), 500
