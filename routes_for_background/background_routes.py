from flask import Blueprint, request, jsonify, send_from_directory
import os
import uuid
from bl.utils.base64_utils import Base64Utils
from bl.background_bl.background_bl import remove_background, UPLOAD_FOLDER, PROCESSED_FOLDER
from bl.utils.hash import calculate_hash
from dal.db_query import ManageQuery
# comment


background_blueprint = Blueprint("background_blueprint", __name__)

# Проверка и создание необходимых папок
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)


@background_blueprint.route("/human", methods=["POST"])
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

    try:
        # Декодируем base64
        decode_image = Base64Utils.decode_base64_in_image(photo_base64)

        # Проверяем уникальность по хэшу
        file_hash = calculate_hash(decode_image)
        if not ManageQuery.is_photo_users_unique(file_hash):
            return jsonify({"error": "Photo already exists"}), 400

        # Генерируем уникальное имя файла
        # Декодируем base64 и сохраняем изображение
        try:
            input_path = Base64Utils.writing_file_background(photo_base64)
        except Exception as e:
            return jsonify({"error": f"Failed to save image: {str(e)}"}), 500

        # Удаляем фон
        output_filename = remove_background(input_path)

        if output_filename:
            # Путь к обработанному изображению
            processed_path = os.path.join(PROCESSED_FOLDER, output_filename)

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


@background_blueprint.route("/processed/<filename>", methods=["GET"])
def get_processed_image(filename):
    """
    Возвращает обработанное изображение по ссылке.
    """
    return send_from_directory(PROCESSED_FOLDER, filename)
