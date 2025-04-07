from flask import Blueprint, request, jsonify
import bl.clothes_bl.clothes_bl as clothes_bl
from dal.db_query import ManageQuery
from bl.utils.check_args import CheckArgs

recovery_photos = Blueprint("recovery_photos", __name__)


@recovery_photos.route("/wardrobe/recovery_photos", methods=["POST"])
def recovery_photos_wardrobe():
    """
    Восстановление фото в гардеробе
    :return: JSON с результатом операции
    """
    try:
        ret = None
        # Получаем данные из JSON
        id_clothes, user_name = clothes_bl.get_data_from_json_recovery_photos(request.json)

        # # Проверка необходимых данных
        # result = CheckArgs.check_args_recovery_photos(id_clothes, user_name)
        # if result["status"] == "error":
        #     return jsonify(result), 400
        #
        # id_user = ManageQuery.get_id_user(user_name)
        # if id_user is None:
        #     return jsonify({"error": f"user_name '{user_name}' не найден"}), 404
        #
        # if not ManageQuery.is_photo_clothes_deleted(id_clothes):
        #     return jsonify({"error": f"Фото одежды с id {id_clothes} уже удалено"}), 400

        ret = CheckArgs.check_args_recovery_photos_wardrobe(id_clothes, user_name)
        if ret["status"] == "error":
            return jsonify(ret), 400

        id_user = ManageQuery.get_id_user(user_name)
        result = ManageQuery.recovery_photos_wardrobe_db(id_clothes, id_user)
        if result['status'] == 'error':
            ret = jsonify(result), 500
        else:
            ret = jsonify(result), 200

        return ret
    except Exception as e:
        return jsonify({"error": f"Ошибка обработки запроса: {str(e)}"}), 500
