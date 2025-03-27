from flask import Blueprint, request, jsonify, send_from_directory
import os
from bl.utils.base64_utils import Base64Utils
from bl.clothes_bl.clothes_bl import remove_background_clothes, UPLOAD_FOLDER, PROCESSED_FOLDER
from dal.db_query import ManageQuery
from bl.utils.hash import calculate_hash

clothes_blueprint = Blueprint("clothes_blueprint", __name__)

# Проверка и создание необходимых папок
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)


@clothes_blueprint.route("/clothes", methods=["POST"])
def process_clothes():
    """
    Принимает изображение в формате base64, удаляет фон и возвращает Base64-изображение без фона.
    """
    # Получаем данные из JSON
    data = request.json
    photo_base64 = data.get("image")
    user_name = data.get("user_name")
    category = data.get("category")
    subcategory = data.get("subcategory")
    sub_subcategory = data.get("sub_subcategory")

    # Проверка необходимых данных
    if not user_name:
        return jsonify({"error": "Отсутствует параметр user_name"}), 400
    if not photo_base64:
        return jsonify({"error": "Отсутствует параметр photo (base64)"}), 400
    if not category:
        return jsonify({"error": "Отсутствует параметр category"}), 400
    if not subcategory:
        return jsonify({"error": "Отсутствует параметр subcategory"}), 400
    if not sub_subcategory:
        return jsonify({"error": "Отсутствует параметр sub_subcategory"}), 400

    try:

        # Декодируем base64
        decode_image = Base64Utils.decode_base64_in_image(photo_base64)

        # Проверяем уникальность по хэшу
        file_hash = calculate_hash(decode_image)

        if not ManageQuery.is_photo_unique(file_hash):
            return jsonify({"error": "Photo already exists"}), 400

        input_path = Base64Utils.writing_file(photo_base64)

        # Удаляем фон
        output_filename = remove_background_clothes(input_path)

        if output_filename:
            # Путь к обработанному изображению
            processed_path = os.path.join(PROCESSED_FOLDER, output_filename)

            # Сохраняем информацию о фотографии пользователя
            try:
                id_clothes = ManageQuery.add_photo_clothes(user_name=user_name, photo_path=processed_path,
                                                           category=category, subcategory=subcategory,
                                                           sub_subcategory=sub_subcategory, is_cut=True)
                if id_clothes:
                    ManageQuery.add_hash_photos_clothes(id_clothes, file_hash)
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


@clothes_blueprint.route("/clothes/processed/<filename>", methods=["GET"])
def get_processed_image(filename):
    """
    Возвращает обработанное изображение по ссылке.
    """
    return send_from_directory(PROCESSED_FOLDER, filename)
