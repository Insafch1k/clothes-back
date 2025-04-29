from flask import Blueprint, request, jsonify
from dal.db_query import ManageQuery
from flask_jwt_extended import jwt_required, get_jwt_identity

recovery_photos = Blueprint("recovery_photos", __name__)


@recovery_photos.route("/wardrobe/recovery_photos", methods=["POST"])
@jwt_required()
def recovery_photos_wardrobe():
    """
    Восстановление фото в гардеробе
    :return: JSON с результатом операции
    """
    try:
        # Получаем ID текущего пользователя из JWT токена
        current_id_user = get_jwt_identity()

        # Получаем данные из JSON
        id_clothes = request.json.get('id_clothes')

        if not id_clothes:
            return jsonify({
                "status": "error",
                "message": "Clothes ID is required"
            }), 400

        # Проверяем существование фото у текущего пользователя
        if not ManageQuery.exist_id_clothes(id_clothes, current_id_user):
            return jsonify({
                "status": "error",
                "message": f"Clothes with ID {id_clothes} not found"
            }), 404

        # Проверяем, что фото действительно удалено
        if not ManageQuery.is_clothes_deleted(id_clothes, current_id_user):
            return jsonify({
                "status": "error",
                "message": f"Clothes with ID {id_clothes} is not deleted"
            }), 400

        # Восстанавливаем фото
        result = ManageQuery.recovery_photos_wardrobe_db(id_clothes, current_id_user)
        if result['status'] == 'error':
            ret = jsonify(result), 500
        else:
            ret = jsonify(result), 200

        return ret
    except Exception as e:
        return jsonify({"error": f"Error processing request: {str(e)}"}), 500
