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
    user_name = data.get("user_name")
    category = data.get("category")
    subcategory = data.get("subcategory")
    sub_subcategory = data.get("sub_subcategory")


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

            # Сохраняем информацию о фотографии пользователя
            try:
                success = ManageQuery.add_photo_clothes(user_name=user_name, photo_path=processed_path, category=category, subcategory=subcategory, sub_subcategory=sub_subcategory, is_cut=True)
                if success:
                    return jsonify({
                        "status": "success",
                        "message": "Фон успешно удален",
                        "image_base64": f"data:image/png;base64,{photo_base64}"
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

@clothes_blueprint.route("/clothes/catalog/<user_name>/<category>/<sub_subcategory>", methods=["GET"])
def get_clothes_by_category_and_sub_subcategory(user_name, category, sub_subcategory):
    """
    Возвращает список одежды из каталога по указанной категории и под подкатегории.
    """
    try:
        id_user = ManageQuery.get_id_user(user_name)
        if id_user is None:
            return jsonify({"error": f"user_name '{user_name}' не найден"}), 404

        id_category = ManageQuery.get_id_category_clothes(category)
        if id_category is None:
            return jsonify({"error": f"Категория '{category}' не найдена"}), 404

        id_sub_subcategory = ManageQuery.get_id_sub_subcategory_clothes(sub_subcategory)
        if id_sub_subcategory is None:
            return jsonify({"error": f"Подподкатегории '{sub_subcategory}' не найдена"}), 404

        clothes_list = ManageQuery.get_clothes_by_category_and_sub_subcategory(id_user=id_user, id_category=id_category, id_sub_subcategory=id_sub_subcategory)
        if not clothes_list:
            return jsonify({"error": f"Одежда в категории '{category}' и в подподкатегори '{sub_subcategory}' не найдена"}), 404

        # result = []
        # for item in clothes_list:
        #     result.append({
        #         "id": item["id_clothes"],
        #         "userId": item["userId"],
        #         "photo_path": item["photo_path"],
        #         "is_cut": item["is_cut"]
        #     })
        for i in range(len(clothes_list)):
            clothes_list[i] = encode_to_base64(clothes_list[i])

        return jsonify({
            "status": "success",
            "message": f"Найдено {len(clothes_list)} элементов в категории '{category}' и подкатегории '{sub_subcategory}'",
            "clothes": clothes_list
        }), 200

    except Exception as error:
        return jsonify({"error": f"Ошибка при обработке запроса: {str(error)}"}), 500
