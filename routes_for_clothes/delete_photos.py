from flask import Blueprint, request, jsonify
from dal.db_query import ManageQuery
from bl.utils.check_args import CheckArgs

delete_photos = Blueprint("delete_photos", __name__)


@delete_photos.route("/wardrobe/delete/<id_clothes>", methods=["DELETE"])
def delete_photo_clothes(id_clothes):
    """
    Удаляет фото одежды из гардероба пользователя
    :param id_clothes: id фото одежды
    :return: JSON с результатом операции
    """
    try:
        ret = None

        result = ManageQuery.delete_photo_clothes(id_clothes)

        if result["status"] == "success":
            ret = jsonify({
                "status": "success",
                "message": f"Фото одежды с id {id_clothes} успешно удалено",
                "id": result["id"]
            }), 200

        elif result["status"] == "error":
            ret = jsonify({
                "status": "error",
                "message": result["message"],
                "id": id_clothes
            }), 404 if 'не найдена' in result['message'] else 400

        return ret
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Внутренняя ошибка сервера: {str(e)}",
            "id": id_clothes
        }), 500


@delete_photos.route("/catalog/delete/<id_clothes>", methods=["DELETE"])
def delete_photo_clothes_catalog(id_clothes):
    """
    Удаляет фото одежды из каталога
    :param id_clothes: id фото одежды
    :return: JSON с результатом операции
    """
    user_name = request.args.get("user_name", type=str)
    if not user_name:
        return jsonify({
            "status": "error",
            "message": "Отсутствует имя пользователя"
        })
    try:
        ret = None

        is_admin = CheckArgs.check_is_admin(user_name)
        if is_admin["status"] == "error":
            return jsonify(is_admin), 403

        result = ManageQuery.delete_photo_clothes_catalog(id_clothes)

        if result["status"] == "success":
            ret = jsonify({
                "status": "success",
                "message": f"Фото одежды с id {id_clothes} успешно удалено из каталога",
                "id": result["id"]
            }), 200

        elif result["status"] == "error":
            ret = jsonify({
                "status": "error",
                "message": result["message"],
                "id": id_clothes
            }), 404 if 'не найдена' in result['message'] else 400

        return ret
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Внутренняя ошибка сервера: {str(e)}",
            "id": id_clothes
        }), 500
