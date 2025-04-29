from flask import Blueprint, jsonify
from dal.db_query import ManageQuery
from bl.utils.check_args import CheckArgs
from flask_jwt_extended import jwt_required, get_jwt_identity

delete_photos = Blueprint("delete_photos", __name__)


@delete_photos.route("/wardrobe/delete/<id_clothes>", methods=["DELETE"])
@jwt_required()
def delete_photo_clothes(id_clothes):
    """
    Удаляет фото одежды из гардероба пользователя
    :param id_clothes: id фото одежды
    :return: JSON с результатом операции
    """
    try:
        id_user = get_jwt_identity()

        # Проверяем существование записи и принадлежность пользователю
        if not ManageQuery.exist_id_clothes(id_clothes, id_user):
            return jsonify({
                "status": "error",
                "message": f"Clothes with ID {id_clothes} not found for user",
                "id": id_clothes
            }), 404

        result = ManageQuery.delete_photo_clothes(id_clothes, id_user)

        if result["status"] == "success":
            return jsonify({
                "status": "success",
                "message": f"Photo of clothes with ID {id_clothes} successfully deleted",
                "id": result["id"]
            }), 200

        elif result["status"] == "error":
            return jsonify({
                "status": "error",
                "message": result["message"],
                "id": id_clothes
            }), 404 if 'not found' in result['message'] else 400

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Internal Server Error: {str(e)}",
            "id": id_clothes
        }), 500


@delete_photos.route("/catalog/delete/<id_clothes>", methods=["DELETE"])
@jwt_required()
def delete_photo_clothes_catalog(id_clothes):
    """
    Удаляет фото одежды из каталога (только для администраторов)
    :param id_clothes: id фото одежды
    :return: JSON с результатом операции
    """
    try:
        id_user = get_jwt_identity()

        is_admin = CheckArgs.check_is_admin(id_user)
        if is_admin["status"] == "error":
            return jsonify({
                "status": "error",
                "message": "You do not have permission to delete from the directory."
            }), 403

        if not ManageQuery.exist_id_clothes_catalog(id_clothes):
            return jsonify({
                "status": "error",
                "message": f"Clothes with ID {id_clothes} not found in the catalog",
                "id": id_clothes
            }), 404

        result = ManageQuery.delete_photo_clothes_catalog(id_clothes)

        if result["status"] == "success":
            return jsonify({
                "status": "success",
                "message": f"The photo of clothes with ID {id_clothes} has been successfully removed from the catalog",
                "id": result["id"]
            }), 200

        elif result["status"] == "error":
            return jsonify({
                "status": "error",
                "message": result["message"],
                "id": id_clothes
            }), 404 if 'not found' in result['message'] else 400

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Internal Server Error: {str(e)}",
            "id": id_clothes
        }), 500
