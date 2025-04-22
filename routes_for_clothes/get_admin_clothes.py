from flask import Blueprint, jsonify, request
from dal.db_query import ManageQuery
from bl.utils.base64_utils import Base64Utils

get_admin_clothes = Blueprint("get_admin_clothes", __name__)


@get_admin_clothes.route("/catalog/admin", methods=["GET"])
def get_admin_clothes_catalog():
    """
    Возвращает список одежды, добавленной администратором, с поддержкой пагинации.
    """
    try:
        page = request.args.get("page", default=1, type=int)
        limit = request.args.get("limit", default=20, type=int)

        if page < 1 or limit < 1:
            return jsonify({"error": "page and limit must be >= 1"}), 400

        offset = (page - 1) * limit

        clothes_list = ManageQuery.get_admin_clothes(limit=limit, offset=offset)

        if not clothes_list:
            return jsonify({"error": "Одежда, добавленная администратором, не найдена"}), 404

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
        return jsonify({"error": f"Ошибка при обработке запроса: {str(error)}"}), 500
