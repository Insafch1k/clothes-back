from flask import Blueprint, request, jsonify
from dal.db_query import ManageQuery
from flask_jwt_extended import jwt_required, get_jwt_identity

recovery_photos = Blueprint("recovery_photos", __name__)


@recovery_photos.route("/recovery_photos", methods=["POST"])
@jwt_required()
def recovery_photos_users():
    """
    Восстановление фото человека
    :return: JSON с результатом операции
    """
    try:
        # Получаем ID текущего пользователя из JWT токена
        current_id_user = get_jwt_identity()

        # Получаем данные из JSON
        id_photo = request.json.get('id_photo')

        if not id_photo:
            return jsonify({
                "status": "error",
                "message": "Photo ID is required"
            }), 400

        # Проверяем существование фото у текущего пользователя
        if not ManageQuery.exist_id_photo_user(id_photo):
            return jsonify({
                "status": "error",
                "message": f"Photo with ID {id_photo} not found"
            }), 404

        # Проверяем, что фото принадлежит текущему пользователю и удалено
        if not ManageQuery.is_photo_user_deleted(id_photo):
            return jsonify({
                "status": "error",
                "message": f"Photo with ID {id_photo} is not deleted or doesn't belong to you"
            }), 400

        result = ManageQuery.recovery_photos_human_db(id_photo, current_id_user)
        if result['status'] == 'error':
            ret = jsonify(result), 500
        else:
            ret = jsonify(result), 200

        return ret
    except Exception as e:
        return jsonify({"error": f"Error processing request: {str(e)}"}), 500
