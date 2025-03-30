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


@clothes_blueprint.route("/process", methods=["POST"])
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
        if not ManageQuery.is_photo_clothes_unique(file_hash):
            return jsonify({"error": "Photo already exists"}), 400

        # Генерируем уникальное имя файла
        # Декодируем base64 и сохраняем изображение
        # input_path = Base64Utils.writing_file(photo_base64)
        try:
            input_path = Base64Utils.writing_file_clothes(photo_base64)
        except Exception as e:
            return jsonify({"error": f"Failed to save image: {str(e)}"}), 500

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


@clothes_blueprint.route("/delete/<id_clothes>", methods=["DELETE"])
def delete_photo_clothes(id_clothes):
    """
    Удаляет фото одежды из гардероба пользователя
    :param id_clothes: id фото одежды
    :return: JSON с результатом операции
    """
    try:
        ret = None

        result = ManageQuery.delete_photo_clothes(id_clothes)

        if result["status"] == "success":
            ret = jsonify({
                "status": "success",
                "message": f"Фото одежды с id {id_clothes} успешно удалено",
                "id": result["id"]
            }), 200

        elif result["status"] == "error":
            ret = jsonify({
                "status": "error",
                "message": result["message"],
                "id": id_clothes
            }), 404 if 'не найдена' in result['message'] else 400

        return ret
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Внутренняя ошибка сервера: {str(e)}",
            "id": id_clothes
        }), 500


@clothes_blueprint.route("/processed/<filename>", methods=["GET"])
def get_processed_image(filename):
    """
    Возвращает обработанное изображение по ссылке.
    """
    return send_from_directory(PROCESSED_FOLDER, filename)


@clothes_blueprint.route("/wardrobe/<user_name>/<category>/<sub_subcategory>", methods=["GET"])
def get_clothes_from_wardrobe(user_name, category, sub_subcategory):
    """
    Возвращает список одежды из гардероба по указанной категории и под подкатегории.
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

        clothes_list = ManageQuery.get_clothes_from_wardrobe(id_user=id_user, id_category=id_category,
                                                             id_sub_subcategory=id_sub_subcategory)
        if not clothes_list:
            return jsonify(
                {"error": f"Одежда в категории '{category}' и в подподкатегори '{sub_subcategory}' не найдена"}), 404

        for i in range(len(clothes_list)):
            clothes_list[i] = Base64Utils.encode_to_base64(clothes_list[i])

        return jsonify({
            "status": "success",
            "message": f"Найдено {len(clothes_list)} элементов в категории '{category}' и подкатегории '{sub_subcategory}'",
            "clothes": clothes_list
        }), 200

    except Exception as error:
        return jsonify({"error": f"Ошибка при обработке запроса: {str(error)}"}), 500


@clothes_blueprint.route("/catalog/<category>/<sub_subcategory>", methods=["GET"])
def get_clothes_from_catalog(category, sub_subcategory):
    """
    Возвращает список одежды из каталога по указанной категории и под подкатегории.
    """
    try:
        id_category = ManageQuery.get_id_category_clothes(category)
        if id_category is None:
            return jsonify({"error": f"Категория '{category}' не найдена"}), 404

        id_sub_subcategory = ManageQuery.get_id_sub_subcategory_clothes(sub_subcategory)
        if id_sub_subcategory is None:
            return jsonify({"error": f"Подподкатегории '{sub_subcategory}' не найдена"}), 404

        clothes_list = ManageQuery.get_clothes_from_catalog(id_category=id_category,
                                                            id_sub_subcategory=id_sub_subcategory)
        if not clothes_list:
            return jsonify(
                {"error": f"Одежда в категории '{category}' и в подподкатегори '{sub_subcategory}' не найдена"}), 404

        for i in range(len(clothes_list)):
            clothes_list[i] = Base64Utils.encode_to_base64(clothes_list[i])

        return jsonify({
            "status": "success",
            "message": f"Найдено {len(clothes_list)} элементов в категории '{category}' и подкатегории '{sub_subcategory}'",
            "clothes": clothes_list
        }), 200

    except Exception as error:
        return jsonify({"error": f"Ошибка при обработке запроса: {str(error)}"}), 500
