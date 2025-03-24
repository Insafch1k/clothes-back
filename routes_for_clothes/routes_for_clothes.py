from flask import Blueprint, request, jsonify, send_from_directory
import os
import uuid
from bl.utils.base64_utils import decode_base64, encode_to_base64
from bl.clothes_bl.clothes_bl import remove_background_clothes, UPLOAD_FOLDER, PROCESSED_FOLDER
from dal.db_query import ManageQuery

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
    user_name = data.get("userId")
    subcategory = data.get("type")


    # Проверка необходимых данных
    if not user_name:
        return jsonify({"error": "Отсутствует параметр user_name"}), 400
    if not photo_base64:
        return jsonify({"error": "Отсутствует параметр photo (base64)"}), 400
    if not subcategory:
        return jsonify({"error": "Отсутствует параметр subcategory"}), 400

    try:
        # Генерируем уникальное имя файла
        filename = f"{uuid.uuid4().hex}.png"
        input_path = os.path.join(UPLOAD_FOLDER, filename)

        # Декодируем base64 и сохраняем изображение
        try:
            decode_base64(photo_base64, input_path)
        except Exception as decode_error:
            return jsonify({"error": str(decode_error)}), 500

        # Удаляем фон
        output_filename = remove_background_clothes(input_path)

        if output_filename:
            # Путь к обработанному изображению
            processed_path = os.path.join(PROCESSED_FOLDER, output_filename)

            # Кодируем обработанное изображение в Base64
            try:
                encoded_image = encode_to_base64(processed_path)
            except Exception as encode_error:
                return jsonify({"error": str(encode_error)}), 500

            # Сохраняем информацию о фотографии пользователя
            try:
                success = ManageQuery.add_photo_clothes(user_name=user_name, photo_path=processed_path, subcategory=subcategory, is_cut=True)
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


@clothes_blueprint.route("/clothes/processed/<filename>", methods=["GET"])
def get_processed_image(filename):
    """
    Возвращает обработанное изображение по ссылке.
    """
    return send_from_directory(PROCESSED_FOLDER, filename)

@clothes_blueprint.route("/clothes/catalog/<subcategory>", methods=["GET"])
def get_clothes_by_category(subcategory):
    """
    Возвращает список одежды из каталога по указанной подкатегории.
    """
    try:
        id_subcategory = ManageQuery.get_id_subcategory_clothes(subcategory)

        if not id_subcategory:
            return jsonify({"error": f"Подкатегория '{subcategory}' не найдена"}), 404

        clothes_list = ManageQuery.get_clothes_by_subcategory(id_subcategory)

        if not clothes_list:
            return jsonify({"error": f"Одежда в подкатегории '{subcategory}' не найдена"}), 404

        result = []
        for item in clothes_list:
            result.append({
                "id": item["id"],
                "user_name": item["user_name"],
                "photo_path": item["photo_path"],
                "is_cut": item["is_cut"]
            })

        return jsonify({
            "status": "success",
            "message": f"Найдено {len(result)} элементов в подкатегории '{subcategory}'",
            "clothes": result
        }), 200

    except Exception as error:
        return jsonify({"error": f"Ошибка при обработке запроса: {str(error)}"}), 500