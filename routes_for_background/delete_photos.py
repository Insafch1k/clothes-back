from flask import Blueprint, jsonify
from dal.db_query import ManageQuery
from flask_jwt_extended import jwt_required, get_jwt_identity

delete_photos = Blueprint("delete_photos", __name__)


@delete_photos.route("/delete/<id_photo>", methods=["DELETE"])
@jwt_required()
def delete_photo_user(id_photo):
    """
    Удаляет фото пользователя
    :param id_photo: id фото пользователя
    :return: JSON с результатом операции
    """
    try:
        id_user = get_jwt_identity()
        # Проверяем, принадлежит ли фото пользователю
        result = ManageQuery.delete_photo_user(id_photo, id_user)

        if result["status"] == "success":
            return jsonify({
                "status": "success",
                "message": f"User photo with ID {id_photo} successfully removed",
                "id": result["id"]
            }), 200

        elif result["status"] == "error":
            return jsonify({
                "status": "error",
                "message": result["message"],
                "id": id_photo
            }), 404 if 'not found' in result['message'] else 400

        return result
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Internal Server Error: {str(e)}",
            "id": id_photo
        }), 500
