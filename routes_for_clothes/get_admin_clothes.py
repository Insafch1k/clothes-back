from flask import Blueprint, jsonify, request
from dal.db_query import ManageQuery
from bl.utils.base64_utils import Base64Utils
from bl.utils.check_args import CheckArgs
from flask_jwt_extended import jwt_required, get_jwt_identity

get_admin_clothes = Blueprint("get_admin_clothes", __name__)


@get_admin_clothes.route("/catalog/admin", methods=["GET"])
@jwt_required()
def get_admin_clothes_catalog():
    """
    Возвращает список одежды, добавленной администратором, с поддержкой пагинации.
    """
    try:
        id_user = get_jwt_identity()

        is_admin = CheckArgs.check_is_admin(id_user)
        if is_admin["status"] == "error":
            return jsonify({
                "status": "error",
                "message": "You do not have permission to delete from the directory."
            }), 403

        page = request.args.get("page", default=1, type=int)
        limit = request.args.get("limit", default=20, type=int)

        if page < 1 or limit < 1:
            return jsonify({"error": "page and limit must be >= 1"}), 400

        offset = (page - 1) * limit

        clothes_list = ManageQuery.get_admin_clothes(limit=limit, offset=offset)

        if not clothes_list:
            return jsonify({"error": "Clothes added by administrator not found"}), 404

        dates = [
            {
                "id_clothes": date[0],
                "photo_path": Base64Utils.encode_to_base64(date[1]),
                "category": ManageQuery.get_name_category(date[2]),
                "subcategory": ManageQuery.get_name_subcategory(date[3]),
                "sub_subcategory": ManageQuery.get_name_sub_subcategory(date[4]),
            }
            for date in clothes_list
        ]

        return jsonify({
            "page": page,
            "limit": limit,
            "total_photos": ManageQuery.count_admin_clothes(),
            "date": dates
        }), 200

    except Exception as error:
        return jsonify({"error": f"Error processing request: {str(error)}"}), 500
