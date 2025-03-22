from flask import Blueprint, request, jsonify, send_from_directory
import os
import uuid
import base64
from bl.background_removal.background_removal import remove_background, UPLOAD_FOLDER, PROCESSED_FOLDER
from dal.db_query import ManageQuery

background_bp = Blueprint("background", __name__)

# Проверка и создание необходимых папок
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

@background_bp.route("/human", methods=["POST"])
def upload_file():
    """
    Принимает изображение в формате base64, удаляет фон и возвращает Base64-изображение без фона.
    """
    # Получаем данные из JSON
    data = request.json
    user_name = data.get("user_name")
    photo_base64 = data.get("photo")

    # Проверка необходимых данных
    if not user_name:
        return jsonify({"error": "Отсутствует параметр user_name"}), 400
    if not photo_base64:
        return jsonify({"error": "Отсутствует параметр photo (base64)"}), 400

    try:
        # Генерируем уникальное имя файла
        filename = f"{uuid.uuid4().hex}.png"
        input_path = os.path.join(UPLOAD_FOLDER, filename)

        # Декодируем base64 и сохраняем изображение
        try:
            image_data = base64.b64decode(photo_base64)
            with open(input_path, "wb") as img_file:
                img_file.write(image_data)
        except Exception as decode_error:
            return jsonify({"error": f"Ошибка декодирования base64: {str(decode_error)}"}), 500

        # Удаляем фон
        output_filename = remove_background(input_path)

        if output_filename:
            # Путь к обработанному изображению
            processed_path = os.path.join(PROCESSED_FOLDER, output_filename)

            # Кодируем обработанное изображение в Base64
            try:
                with open(processed_path, "rb") as img_file:
                    encoded_image = base64.b64encode(img_file.read()).decode('utf-8')
            except Exception as encode_error:
                return jsonify({"error": f"Ошибка кодирования Base64: {str(encode_error)}"}), 500

            # Сохраняем информацию о фотографии пользователя
            try:
                success = ManageQuery.add_photo_user(user_name=user_name, photo_path=processed_path, category="full", is_cut=True)
                if success:
                    return jsonify({
                        "status": "success",
                        "message": "Фон успешно удален",
                        "image_base64": f"data:image/png;base64,{encoded_image}"
                    })
                else:
                    return jsonify({"error": "Ошибка сохранения данных в БД"}), 500
            except Exception as db_error:
                return jsonify({"error": f"Ошибка при работе с БД: {str(db_error)}"}), 500
        else:
            return jsonify({"error": "Ошибка обработки изображения"}), 500
    except Exception as error:
        return jsonify({"error": f"Ошибка обработки запроса: {str(error)}"}), 500


@background_bp.route("/processed/<filename>", methods=["GET"])
def get_processed_image(filename):
    """
    Возвращает обработанное изображение по ссылке.
    """
    return send_from_directory(PROCESSED_FOLDER, filename)

