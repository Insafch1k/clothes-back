from flask import Blueprint, request, jsonify
from bl.utils.base64_utils import Base64Utils
from bl.background_bl.background_bl import remove_background
from bl.utils.create_folders import create_folders_for_background
from bl.utils.hash import calculate_hash
import config
from dal.db_query import ManageQuery
from flask_jwt_extended import jwt_required, get_jwt_identity
import bl.background_bl.background_bl as background_bl

add_photos = Blueprint("add_photos", __name__)

create_folders_for_background()


@add_photos.route("/process", methods=["POST"])
@jwt_required()
def upload_file():
    """
    Принимает изображение в формате base64, удаляет фон и возвращает Base64-изображение без фона.
    """
    try:
        # Получаем текущего пользователя из JWT
        id_user = get_jwt_identity()

        # Получаем данные из JSON
        photo_base64 = request.json.get("image")
        if not photo_base64:
            return jsonify({"error": "Missing parameter photo (base64)"}), 400

        # Проверка уникальности
        decode_image = Base64Utils.decode_base64_in_image(photo_base64)
        file_hash = calculate_hash(decode_image)
        if not ManageQuery.is_photo_users_unique(file_hash, id_user):
            return jsonify({"error": "Photo already exists"}), 400

        # Проверяем, есть ли уже такое фото у пользователя среди удалённых
        id_photo = ManageQuery.is_photo_user_among_deleted(file_hash, id_user)
        if id_photo:
            result = ManageQuery.recovery_photos_human_db(id_photo, id_user)
            if result['status'] == 'error':
                return jsonify(result), 500
            else:
                return jsonify(result), 200

        # Обработка фото
        processed_path, file_hash, error_response, status_code = background_bl.process_photo_common(
            photo_base64,
            Base64Utils.writing_file_background,
            remove_background,
            config.PROCESSED_FOLDER_BACKGROUND
        )
        if error_response:
            return error_response, status_code

        # Сохранение в БД
        encode_image, error_response, status_code = background_bl.save_photo_to_db(
            processed_path,
            file_hash,
            id_user,
            ManageQuery.add_hash_photos_users
        )
        if error_response:
            return error_response, status_code

        return jsonify({
            "status": "success",
            "message": "Background successfully removed",
            "image_base64": f"data:image/png;base64,{encode_image}"
        })
    except Exception as error:
        return jsonify({"error": f"Error processing request: {str(error)}"}), 500
