from flask import Blueprint, request, jsonify
from bl.clothes_bl import clothes_bl
from flask_jwt_extended import jwt_required, get_jwt_identity

get_wardrobe_catalog = Blueprint("get_wardrobe_catalog", __name__)


@get_wardrobe_catalog.route("/wardrobe/<category>/<subcategory>/<sub_subcategory>", methods=["GET"])
@jwt_required()
def get_clothes_from_wardrobe(category, subcategory, sub_subcategory):
    """
    Возвращает список одежды из гардероба по категории, подкатегории и под_подкатегории.
    """
    try:
        id_user = get_jwt_identity()
        page = request.args.get("page", default=1, type=int)
        limit = request.args.get("limit", default=20, type=int)

        # Проверка параметров
        if page < 1 or limit < 1:
            return jsonify({"error": "page and limit must be >= 1"}), 400

        # Получение списка
        response, status_code = clothes_bl.get_clothes_by_type(
            source="wardrobe",
            id_user=id_user,
            category=category,
            subcategory=subcategory,
            sub_subcategory=sub_subcategory,
            page=page,
            limit=limit
        )
        return response, status_code

    except Exception as error:
        return jsonify({"error": f"Error processing request: {str(error)}"}), 500


@get_wardrobe_catalog.route("/catalog/<category>/<subcategory>/<sub_subcategory>", methods=["GET"])
def get_clothes_from_catalog(category, subcategory, sub_subcategory):
    """
    Возвращает список одежды из каталога по указанной категории, подкатегории и под_подкатегории.
    """
    try:
        page = request.args.get("page", default=1, type=int)
        limit = request.args.get("limit", default=20, type=int)

        # Проверка параметров
        if page < 1 or limit < 1:
            return jsonify({"error": "page and limit must be >= 1"}), 400

        response, status_code = clothes_bl.get_clothes_by_type(
            source="catalog",
            id_user=None,
            category=category,
            subcategory=subcategory,
            sub_subcategory=sub_subcategory,
            page=page,
            limit=limit
        )
        return response, status_code

    except Exception as error:
        return jsonify({"error": f"Error processing request: {str(error)}"}), 500
