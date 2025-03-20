from flask import Blueprint, request, jsonify, send_from_directory
import os
import uuid
import base64
from bl.background_removal.background_removal import remove_background, UPLOAD_FOLDER, PROCESSED_FOLDER
from dal.db_query import ManageQuery
from PIL import Image

background_bp = Blueprint("background", __name__)

# Проверка и создание необходимых папок
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

@background_bp.route("/upload", methods=["POST"])
def upload_file():
    """
    Принимает изображение, удаляет фон и возвращает ссылку на файл.
    """
    user_name = request.form.get("user_name")
    photo = request.files.get("photo")

    # Проверка необходимых данных
    if not user_name:
        return jsonify({"error": "Отсутствует параметр user_name"})
    if not photo:
        return jsonify({"error": "Отсутствует файл photo"})

    try:
        # Генерируем уникальное имя файла и сохраняем его
        filename = f"{uuid.uuid4().hex}.png"
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        photo.save(input_path)

        # Удаляем фон
        output_filename = remove_background(input_path)

        if output_filename:
            # Читаем изображение и кодируем в Base64 (если это необходимо для других целей)
            # with open(input_path, "rb") as img_file:
            #     image_data = img_file.read()

            # Сохраняем информацию о фотографии пользователя
            try:
                success = ManageQuery.add_photo_user(user_name=user_name, photo_path=input_path, category="full", is_cut=True)
                if success:
                    return jsonify({
                        "message": "Фон удалён!",
                        "file_url": f"/background/processed/{output_filename}"
                    })
                else:
                    return jsonify({"error": "Ошибка сохранения данных в БД"})
            except Exception as db_error:
                return jsonify({"error": f"Ошибка при работе с БД: {str(db_error)}"})
        else:
            return jsonify({"error": "Ошибка обработки изображения"})
    except Exception as error:
        return jsonify({"error": f"Ошибка обработки запроса: {str(error)}"})

@background_bp.route("/processed/<filename>", methods=["GET"])
def get_processed_image(filename):
    """
    Возвращает обработанное изображение по ссылке.
    """
    return send_from_directory(PROCESSED_FOLDER, filename)