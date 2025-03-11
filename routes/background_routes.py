from flask import Blueprint, request, jsonify, send_from_directory
import os
from bl.background_removal.background_removal import remove_background, UPLOAD_FOLDER, PROCESSED_FOLDER
from dal.db_query import ManageQuery
from dotenv import load_dotenv, find_dotenv

background_bp = Blueprint("background", __name__)

# Если папки ещё не созданы, можно проверить
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

@background_bp.route("/upload", methods=["POST"])
def upload_file():
    """
    Принимает изображение, удаляет фон и возвращает ссылку на файл
    """
    if "file" not in request.files:
        return jsonify({"error": "Файл не найден!"})

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Файл не выбран!"})

    # Сохраняем загруженный файл в папку uploads внутри bl/background_removal
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    # Удаляем фон
    output_filename = remove_background(input_path)

    if output_filename:
        success = ManageQuery.add_photo_user(user_name="test_name", photo=open(input_path, "rb").read(), category="full")
        if success:
            return jsonify({"message": "Фон удалён!", "file_url": f"/background/processed/{output_filename}"})
        else:
            return jsonify({"error": "Ошибка обработки изображения"})
    else:
        return jsonify({"error": "Ошибка обработки изображения"})


@background_bp.route("/processed/<filename>", methods=["GET"])
def get_processed_image(filename):
    """
    Возвращает обработанное изображение по ссылке
    """
    return send_from_directory(PROCESSED_FOLDER, filename)