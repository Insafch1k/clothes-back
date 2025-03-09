from flask import Blueprint, request, jsonify, send_from_directory
import os
from background_removal import remove_background

background_bp = Blueprint("background", __name__)
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed_images"


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

    # Сохраняем загруженный файл
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    # Удаляем фон
    output_filename = remove_background(input_path)

    if output_filename:
        return jsonify({"message": "Фон удалён!", "file_url": f"/processed/{output_filename}"})
    else:
        return jsonify({"error": "Ошибка обработки изображения"})

@background_bp.route("/processed/<filename>", methods=["GET"])
def get_processed_image(filename):
    """
    Возвращает обработанное изображение по ссылке
    """
    return send_from_directory(PROCESSED_FOLDER, filename)
