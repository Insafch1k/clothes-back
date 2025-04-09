from flask import Blueprint, request, jsonify
from dal.db_query import ManageQuery
from bl.utils.base64_utils import Base64Utils

get_photos = Blueprint("get_photos", __name__)


@get_photos.route("/user_photos/<user_name>", methods=["GET"])
def get_user_photos(user_name):  # user_name из URL!
    # Пагинация — в query-параметрах
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=20, type=int)

    if page < 1 or limit < 1:
        return jsonify({"error": "page and limit must be >= 1"}), 400

    try:
        id_user = ManageQuery.get_id_user(user_name)
        if not id_user:
            return jsonify({"error": "User not found"}), 404

        photos = ManageQuery.get_user_photos_paginated(
            id_user=id_user,
            limit=limit,
            offset=(page - 1) * limit
        )

        photos_with_base64 = [
            {
                "id": photo[0],
                # "photo_path": photo["photo_path"],
                "image_base64": Base64Utils.encode_to_base64(photo[1])
            }
            for photo in photos
        ]

        return jsonify({
            "page": page,
            "limit": limit,
            "total_photos": ManageQuery.count_user_photos(id_user),
            "photos": photos_with_base64
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
