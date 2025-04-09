from flask import Blueprint, request, jsonify
from dal.db_query import ManageQuery

delete_photos = Blueprint("delete_photos", __name__)


@delete_photos.route("/delete/<id_photo>", methods=["DELETE"])
def delete_photo_user(id_photo):
    """
    Удаляет фото пользователя
    :param id_photo: id фото пользователя
    :return: JSON с результатом операции
    """
    try:
        ret = None

        result = ManageQuery.delete_photo_user(id_photo)

        if result["status"] == "success":
            ret = jsonify({
                "status": "success",
                "message": f"Фото пользователя с id {id_photo} успешно удалено",
                "id": result["id"]
            }), 200

        elif result["status"] == "error":
            ret = jsonify({
                "status": "error",
                "message": result["message"],
                "id": id_photo
            }), 404 if 'не найдена' in result['message'] else 400

        return ret
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Внутренняя ошибка сервера: {str(e)}",
            "id": id_photo
        }), 500
