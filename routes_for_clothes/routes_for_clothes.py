from flask import Blueprint, request, jsonify, send_from_directory
import os
from bl.utils.base64_utils import Base64Utils
# from bl.clothes_bl.clothes_bl import remove_background_clothes, UPLOAD_FOLDER_, PROCESSED_FOLDER, \
#     PROCESSED_FOLDER_CATALOG, remove_background_clothes_catalog
from dal.db_query import ManageQuery
from bl.utils.hash import calculate_hash
from bl.utils.check_args import CheckArgs

clothes_blueprint = Blueprint("clothes_blueprint", __name__)
"""
Этот файл разделяется на более мелкие, поэтому скоро удалится
"""


# # Проверка и создание необходимых папок
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)
# if not os.path.exists(PROCESSED_FOLDER):
#     os.makedirs(PROCESSED_FOLDER)


# @clothes_blueprint.route("/process", methods=["POST"])
# def process_clothes():
#     """
#     Принимает изображение в формате base64, удаляет фон и возвращает Base64-изображение без фона.
#     """
#     # Получаем данные из JSON
#     data = request.json
#     photo_base64 = data.get("image")
#     user_name = data.get("user_name")
#     category = data.get("category")
#     subcategory = data.get("subcategory")
#     sub_subcategory = data.get("sub_subcategory")
#
#     # Проверка необходимых данных
#     if not user_name:
#         return jsonify({"error": "Отсутствует параметр user_name"}), 400
#     if not photo_base64:
#         return jsonify({"error": "Отсутствует параметр photo (base64)"}), 400
#     if not category:
#         return jsonify({"error": "Отсутствует параметр category"}), 400
#     if not subcategory:
#         return jsonify({"error": "Отсутствует параметр subcategory"}), 400
#     if not sub_subcategory:
#         return jsonify({"error": "Отсутствует параметр sub_subcategory"}), 400
#
#     try:
#
#         # Декодируем base64
#         decode_image = Base64Utils.decode_base64_in_image(photo_base64)
#
#         # Проверяем уникальность по хэшу
#         file_hash = calculate_hash(decode_image)
#         if not ManageQuery.is_photo_clothes_unique(file_hash):
#             return jsonify({"error": "Photo already exists"}), 400
#
#         # Генерируем уникальное имя файла
#         # Декодируем base64 и сохраняем изображение
#         # input_path = Base64Utils.writing_file(photo_base64)
#         try:
#             input_path = Base64Utils.writing_file_clothes(photo_base64)
#         except Exception as e:
#             return jsonify({"error": f"Failed to save image: {str(e)}"}), 500
#
#         # Удаляем фон
#         output_filename = remove_background_clothes(input_path)
#
#         # Удаляем необработанное фото
#         if os.path.exists(input_path):
#             os.remove(input_path)
#
#         if output_filename:
#             # Путь к обработанному изображению
#             processed_path = os.path.join(PROCESSED_FOLDER, output_filename)
#
#             # Сохраняем информацию о фотографии пользователя
#             try:
#                 id_clothes = ManageQuery.add_photo_clothes(user_name=user_name, photo_path=processed_path,
#                                                            category=category, subcategory=subcategory,
#                                                            sub_subcategory=sub_subcategory, is_cut=True)
#                 if id_clothes:
#                     ManageQuery.add_hash_photos_clothes(id_clothes, file_hash)
#                     encode_image = Base64Utils.encode_to_base64(processed_path)
#
#                     return jsonify({
#                         "status": "success",
#                         "message": "Фон успешно удален",
#                         "image_base64": f"data:image/png;base64,{encode_image}"
#                     })
#                 else:
#                     return jsonify({"error": "Ошибка сохранения данных в БД"}), 500
#             except Exception as db_error:
#                 return jsonify({"error": f"Ошибка при работе с БД: {str(db_error)}"}), 500
#         else:
#             return jsonify({"error": "Ошибка обработки изображения"}), 500
#     except Exception as error:
#         return jsonify({"error": f"Ошибка обработки запроса: {str(error)}"}), 500


# @clothes_blueprint.route("/wardrobe/delete/<id_clothes>", methods=["DELETE"])
# def delete_photo_clothes(id_clothes):
#     """
#     Удаляет фото одежды из гардероба пользователя
#     :param id_clothes: id фото одежды
#     :return: JSON с результатом операции
#     """
#     try:
#         ret = None
#
#         result = ManageQuery.delete_photo_clothes(id_clothes)
#
#         if result["status"] == "success":
#             ret = jsonify({
#                 "status": "success",
#                 "message": f"Фото одежды с id {id_clothes} успешно удалено",
#                 "id": result["id"]
#             }), 200
#
#         elif result["status"] == "error":
#             ret = jsonify({
#                 "status": "error",
#                 "message": result["message"],
#                 "id": id_clothes
#             }), 404 if 'не найдена' in result['message'] else 400
#
#         return ret
#     except Exception as e:
#         return jsonify({
#             "status": "error",
#             "message": f"Внутренняя ошибка сервера: {str(e)}",
#             "id": id_clothes
#         }), 500


# @clothes_blueprint.route("/processed/<filename>", methods=["GET"])
# def get_processed_image(filename):
#     """
#     Возвращает обработанное изображение по ссылке.
#     """
#     return send_from_directory(PROCESSED_FOLDER, filename)


# @clothes_blueprint.route("/wardrobe/<user_name>/<category>/<subcategory>/<sub_subcategory>", methods=["GET"])
# def get_clothes_from_wardrobe(user_name, category, subcategory, sub_subcategory):
#     """
#     Возвращает список одежды из гардероба по указанной категории и под подкатегории.
#     """
#     try:
#         page = request.args.get("page", default=1, type=int)
#         limit = request.args.get("limit", default=20, type=int)
#         if page < 1 or limit < 1:
#             return jsonify({"error": "page and limit must be >=1"}), 400
#
#         id_user = ManageQuery.get_id_user(user_name)
#         if id_user is None:
#             return jsonify({"error": f"user_name '{user_name}' не найден"}), 404
#
#         id_category = ManageQuery.get_id_category_clothes(category)
#         if id_category is None:
#             return jsonify({"error": f"Категория '{category}' не найдена"}), 404
#
#         id_subcategory = ManageQuery.get_id_subcategory_clothes(subcategory)
#         if id_subcategory is None:
#             return jsonify({"error": f"Подкатегория '{subcategory}' не найдена"}), 404
#
#         id_sub_subcategory = ManageQuery.get_id_sub_subcategory_clothes(sub_subcategory)
#         if id_sub_subcategory is None:
#             return jsonify({"error": f"Подподкатегории '{sub_subcategory}' не найдена"}), 404
#
#         offset = (page - 1) * limit
#
#         clothes_list = ManageQuery.get_clothes_from_wardrobe_paginated(id_user=id_user, id_category=id_category,
#                                                                        id_subcategory=id_subcategory,
#                                                                        id_sub_subcategory=id_sub_subcategory,
#                                                                        limit=limit, offset=offset)
#         if not clothes_list:
#             return jsonify(
#                 {
#                     "error": f"Одежда в категории '{category}', в подкатегории {subcategory} и в подподкатегори '{sub_subcategory}' не найдена"}), 404
#
#         for i in range(len(clothes_list)):
#             clothes_list[i] = Base64Utils.encode_to_base64(clothes_list[i])
#
#         return jsonify({
#             "status": "success",
#             "message": f"Найдено {len(clothes_list)} элементов в категории '{category}', в подкатегории {subcategory} и подкатегории '{sub_subcategory}'",
#             "pagination": {
#                 "page": page,
#                 "limit": limit,
#                 "total_items": ManageQuery.count_clothes_in_wardrobe(id_user, id_category, id_sub_subcategory)
#             },
#             "clothes": clothes_list
#         }), 200
#
#     except Exception as error:
#         return jsonify({"error": f"Ошибка при обработке запроса: {str(error)}"}), 500
#
#
# @clothes_blueprint.route("/catalog/<category>/<subcategory>/<sub_subcategory>", methods=["GET"])
# def get_clothes_from_catalog(category, subcategory, sub_subcategory):
#     """
#     Возвращает список одежды из каталога по указанной категории и под подкатегории.
#     """
#     try:
#         page = request.args.get("page", default=1, type=int)
#         limit = request.args.get("limit", default=20, type=int)
#
#         if page < 1 or limit < 1:
#             return jsonify({"error": "page and limit must be >=1"}), 400
#
#         id_category = ManageQuery.get_id_category_clothes(category)
#         if id_category is None:
#             return jsonify({"error": f"Категория '{category}' не найдена"}), 404
#
#         id_subcategory = ManageQuery.get_id_subcategory_clothes(subcategory)
#         if id_subcategory is None:
#             return jsonify({"error": f"Подкатегория '{subcategory}' не найдена"}), 404
#
#         id_sub_subcategory = ManageQuery.get_id_sub_subcategory_clothes(sub_subcategory)
#         if id_sub_subcategory is None:
#             return jsonify({"error": f"Подподкатегории '{sub_subcategory}' не найдена"}), 404
#
#         offset = (page - 1) * limit
#
#         clothes_list = ManageQuery.get_clothes_from_catalog_paginated(id_category=id_category,
#                                                                       id_subcategory=id_subcategory,
#                                                                       id_sub_subcategory=id_sub_subcategory,
#                                                                       limit=limit, offset=offset)
#         if not clothes_list:
#             return jsonify(
#                 {
#                     "error": f"Одежда в категории '{category}', в подкатегории {subcategory} и в подподкатегори '{sub_subcategory}' не найдена"}), 404
#
#         for i in range(len(clothes_list)):
#             clothes_list[i] = Base64Utils.encode_to_base64(clothes_list[i])
#
#         return jsonify({
#             "status": "success",
#             "message": f"Найдено {len(clothes_list)} элементов в категории '{category}' и подкатегории '{sub_subcategory}'",
#             "pagination": {
#                 "page": page,
#                 "limit": limit,
#                 "total_items": ManageQuery.count_clothes_in_catalog(id_category, id_sub_subcategory)
#             },
#             "clothes": clothes_list
#         }), 200
#
#     except Exception as error:
#         return jsonify({"error": f"Ошибка при обработке запроса: {str(error)}"}), 500


# @clothes_blueprint.route("/catalog/add_photos", methods=["POST"])
# def add_photos_in_catalog():
#     """
#     Добавление фото в каталог администратором
#     :return: JSON с результатом операции
#     """
#     # Получаем данные из JSON
#     data = request.json
#     photo_base64 = data.get("image")
#     user_name = data.get("user_name")
#     category = data.get("category")
#     subcategory = data.get("subcategory")
#     sub_subcategory = data.get("sub_subcategory")
#
#     result = CheckArgs.check_args_add_photos_in_catalog(photo_base64, user_name, category, subcategory,
#                                                         sub_subcategory)
#     if result["status"] == "error":
#         if "не является администратором" in result["error"]:
#             return jsonify(result), 403
#         else:
#             return jsonify(result), 400
#
#     try:
#
#         # Декодируем base64
#         decode_image = Base64Utils.decode_base64_in_image(photo_base64)
#
#         # Проверяем уникальность по хэшу
#         file_hash = calculate_hash(decode_image)
#         if not ManageQuery.is_photo_catalog_unique(file_hash):
#             return jsonify({"error": "Photo already exists"}), 400
#
#         # Генерируем уникальное имя файла
#         # Декодируем base64 и сохраняем изображение
#         # input_path = Base64Utils.writing_file(photo_base64)
#         try:
#             input_path = Base64Utils.writing_file_clothes_catalog(photo_base64)
#         except Exception as e:
#             return jsonify({"error": f"Failed to save image catalog: {str(e)}"}), 500
#
#         # Удаляем фон
#         output_filename = remove_background_clothes_catalog(input_path)
#
#         # Удаляем необработанное фото
#         if os.path.exists(input_path):
#             os.remove(input_path)
#
#         if output_filename:
#             # Путь к обработанному изображению
#             processed_path = os.path.join(PROCESSED_FOLDER_CATALOG, output_filename)
#
#             # Сохраняем информацию о фотографии пользователя
#             try:
#                 id_clothes = ManageQuery.add_photo_clothes(user_name=user_name, photo_path=processed_path,
#                                                            category=category, subcategory=subcategory,
#                                                            sub_subcategory=sub_subcategory, is_cut=True)
#                 if id_clothes:
#                     ManageQuery.add_hash_photos_clothes_catalog(id_clothes, file_hash)
#                     encode_image = Base64Utils.encode_to_base64(processed_path)
#
#                     return jsonify({
#                         "status": "success",
#                         "message": "Фон успешно удален",
#                         "image_base64": f"data:image/png;base64,{encode_image}"
#                     })
#                 else:
#                     return jsonify({"error": "Ошибка сохранения данных в БД"}), 500
#             except Exception as db_error:
#                 return jsonify({"error": f"Ошибка при работе с БД: {str(db_error)}"}), 500
#         else:
#             return jsonify({"error": "Ошибка обработки изображения"}), 500
#     except Exception as error:
#         return jsonify({"error": f"Ошибка обработки запроса: {str(error)}"}), 500


# @clothes_blueprint.route("/catalog/delete/<id_clothes>", methods=["DELETE"])
# def delete_photo_clothes_catalog(id_clothes):
#     """
#     Удаляет фото одежды из каталога
#     :param id_clothes: id фото одежды
#     :return: JSON с результатом операции
#     """
#     user_name = request.args.get("user_name", type=str)
#     if not user_name:
#         return jsonify({
#             "status": "error",
#             "message": "Отсутствует имя пользователя"
#         })
#     try:
#         ret = None
#
#         is_admin = CheckArgs.check_is_admin(user_name)
#         if is_admin["status"] == "error":
#             return jsonify(is_admin), 403
#
#         result = ManageQuery.delete_photo_clothes_catalog(id_clothes)
#
#         if result["status"] == "success":
#             ret = jsonify({
#                 "status": "success",
#                 "message": f"Фото одежды с id {id_clothes} успешно удалено из каталога",
#                 "id": result["id"]
#             }), 200
#
#         elif result["status"] == "error":
#             ret = jsonify({
#                 "status": "error",
#                 "message": result["message"],
#                 "id": id_clothes
#             }), 404 if 'не найдена' in result['message'] else 400
#
#         return ret
#     except Exception as e:
#         return jsonify({
#             "status": "error",
#             "message": f"Внутренняя ошибка сервера: {str(e)}",
#             "id": id_clothes
#         }), 500


# @clothes_blueprint.route("/try_on/<user_name>/<id_clothes>", methods=["GET"])
# def try_on_clothes(user_name, id_clothes):
#     """
#     Роут-заглушка для кнопки "одеть вещь".
#     Принимает параметры как настоящий роут, но возвращает фото-заглушку.
#     """
#     try:
#         id_user = ManageQuery.get_id_user(user_name)
#         if not id_user:
#             return jsonify({"error": f"user_name '{user_name}' не найден"}), 404
#
#         photo_path = ManageQuery.get_path_clothes(id_clothes)
#         if not photo_path:
#             return jsonify({"error": f"id_clothes '{id_clothes}' не найден"}), 404
#
#         placeholder_image = (
#             "data:image/png;base64,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"
#         )
#
#         # Возвращаем заглушку
#         return jsonify({
#             "status": "success",
#             "message": "Это роут-заглушка. Функционал одевания вещей пока не реализован.",
#             "clothes": placeholder_image
#         }), 200
#
#     except Exception as error:
#         return jsonify({"error": f"Ошибка при обработке запроса: {str(error)}"}), 500


@clothes_blueprint.route("/catalog", methods=["GET"])
def get_admin_clothes_catalog():
    """
    Возвращает список одежды, добавленной администратором, с поддержкой пагинации.
    """
    try:
        page = request.args.get("page", default=1, type=int)
        limit = request.args.get("limit", default=20, type=int)

        if page < 1 or limit < 1:
            return jsonify({"error": "page and limit must be >= 1"}), 400

        offset = (page - 1) * limit

        clothes_list = ManageQuery.get_admin_clothes(limit=limit, offset=offset)

        if not clothes_list:
            return jsonify({"error": "Одежда, добавленная администратором, не найдена"}), 404

        dates = [
            {
                "id_clothes": date[0],
                "photo_path": Base64Utils.encode_to_base64(date[1]),
                "category": ManageQuery.get_name_category(date[2]),
                "subcategory": ManageQuery.get_name_subcategory(date[3]),
                "sub_subcategory": ManageQuery.get_name_sub_subcategory(date[4]),
            }
            for date in clothes_list
        ]

        return jsonify({
            "page": page,
            "limit": limit,
            "total_photos": ManageQuery.count_admin_clothes(),
            "date": dates
        }), 200

    except Exception as error:
        return jsonify({"error": f"Ошибка при обработке запроса: {str(error)}"}), 500
