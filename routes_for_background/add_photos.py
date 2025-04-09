from flask import Blueprint, request, jsonify, send_from_directory
import os
from bl.utils.base64_utils import Base64Utils
from bl.background_bl.background_bl import remove_background
from bl.utils.create_folders import create_folders_for_background
from bl.utils.hash import calculate_hash
from config import PROCESSED_FOLDER_BACKGROUND
from dal.db_query import ManageQuery

add_photos = Blueprint("add_photos", __name__)

create_folders_for_background()


@add_photos.route("/process", methods=["POST"])
def upload_file():
    """
    Принимает изображение в формате base64, удаляет фон и возвращает Base64-изображение без фона.
    """
    # Получаем данные из JSON
    data = request.json
    user_name = data.get("user_name")
    photo_base64 = data.get("image")

    # Проверка необходимых данных
    if not user_name:
        return jsonify({"error": "Отсутствует параметр user_name"}), 400
    if not photo_base64:
        return jsonify({"error": "Отсутствует параметр photo (base64)"}), 400
    id_user = ManageQuery.get_id_user(user_name)
    if not id_user:
        return jsonify({
            "error": f"Пользователь с именем {user_name} не найден"
        }), 400

    try:
        # Декодируем base64
        decode_image = Base64Utils.decode_base64_in_image(photo_base64)

        # Проверяем уникальность по хэшу
        file_hash = calculate_hash(decode_image)
        if not ManageQuery.is_photo_users_unique(file_hash, id_user):
            return jsonify({"error": "Photo already exists"}), 400

        # Проверяем, есть ли уже такое фото у пользователя среди удалённых, если есть, то восстанавливаем его
        id_photo = ManageQuery.is_photo_user_among_deleted(file_hash, id_user)
        if id_photo:
            result = ManageQuery.recovery_photos_human_db(id_photo, id_user)
            if result['status'] == 'error':
                return jsonify(result), 500
            else:
                return jsonify(result), 200

        # Генерируем уникальное имя файла.
        # Декодируем base64 и сохраняем изображение
        try:
            input_path = Base64Utils.writing_file_background(photo_base64)
        except Exception as e:
            return jsonify({"error": f"Failed to save image: {str(e)}"}), 500

        # Удаляем фон
        output_filename = remove_background(input_path)

        # Удаляем необработанное фото
        if os.path.exists(input_path):
            os.remove(input_path)

        if output_filename:
            # Путь к обработанному изображению
            processed_path = os.path.join(PROCESSED_FOLDER_BACKGROUND, output_filename)

            # Сохраняем информацию о фотографии пользователя
            try:
                id_photo = ManageQuery.add_photo_user(user_name=user_name, photo_path=processed_path, category="full",
                                                      is_cut=True)

                if id_photo:
                    ManageQuery.add_hash_photos_users(id_photo, file_hash)
                    encode_image = Base64Utils.encode_to_base64(processed_path)

                    return jsonify({
                        "status": "success",
                        "message": "Фон успешно удален",
                        "image_base64": f"data:image/png;base64,{encode_image}"
                    })
                else:
                    return jsonify({"error": "Ошибка сохранения данных в БД"}), 500
            except Exception as db_error:
                return jsonify({"error": f"Ошибка при работе с БД: {str(db_error)}"}), 500
        else:
            return jsonify({"error": "Ошибка обработки изображения"}), 500
    except Exception as error:
        return jsonify({"error": f"Ошибка обработки запроса: {str(error)}"}), 500
