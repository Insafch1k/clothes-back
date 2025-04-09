from flask import Blueprint, request, jsonify
import bl.background_bl.background_bl as background_bl
from dal.db_query import ManageQuery
from bl.utils.check_args import CheckArgs

recovery_photos = Blueprint("recovery_photos", __name__)


@recovery_photos.route("/recovery_photos", methods=["POST"])
def recovery_photos_human():
    """
    Восстановление фото человека
    :return: JSON с результатом операции
    """
    try:
        # Получаем данные из JSON
        id_photo, user_name = background_bl.get_data_from_json_recovery_photos_human(request.json)

        ret = CheckArgs.check_args_recovery_photos_human(id_photo, user_name)
        if ret["status"] == "error":
            return jsonify(ret), 400

        id_user = ManageQuery.get_id_user(user_name)
        result = ManageQuery.recovery_photos_human_db(id_photo, id_user)
        if result['status'] == 'error':
            ret = jsonify(result), 500
        else:
            ret = jsonify(result), 200

        return ret
    except Exception as e:
        return jsonify({"error": f"Ошибка обработки запроса: {str(e)}"}), 500
