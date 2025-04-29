from flask import Blueprint, request, jsonify
from dal.db_query import ManageQuery
from bl.utils.base64_utils import Base64Utils
from flask_jwt_extended import jwt_required, get_jwt_identity

get_photos = Blueprint("get_photos", __name__)


@get_photos.route("/user_photos", methods=["GET"])
@jwt_required()
def get_user_photos():
    """
    Получение фото текущего пользователя
    """
    try:
        current_id_user = get_jwt_identity()
        page = request.args.get("page", default=1, type=int)
        limit = request.args.get("limit", default=20, type=int)

        if page < 1 or limit < 1:
            return jsonify({"error": "page and limit must be >= 1"}), 400

        photos = ManageQuery.get_user_photos_paginated(
            id_user=current_id_user,
            limit=limit,
            offset=(page - 1) * limit
        )

        photos_with_base64 = [
            {
                "id": photo[0],
                "image_base64": Base64Utils.encode_to_base64(photo[1])
            }
            for photo in photos
        ]

        return jsonify({
            "page": page,
            "limit": limit,
            "total_photos": ManageQuery.count_user_photos(current_id_user),
            "photos": photos_with_base64
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
