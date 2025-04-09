from flask import Blueprint, request, jsonify, send_from_directory
import os
from bl.utils.base64_utils import Base64Utils
import bl.clothes_bl.clothes_bl as clothes_bl
from dal.db_query import ManageQuery
from bl.utils.hash import calculate_hash
from bl.utils.check_args import CheckArgs
import config
from bl.utils.create_folders import create_folders_for_clothes

create_folders_for_clothes()

add_photos = Blueprint("add_photos", __name__)


@add_photos.route("/process", methods=["POST"])
def process_clothes():
    """
    Принимает изображение в формате base64, удаляет фон и возвращает Base64-изображение без фона.
    """
    # Получаем данные из JSON
    photo_base64, user_name, category, subcategory, sub_subcategory = clothes_bl.get_data_from_json_add_photos(
        request.json)

    # Проверка необходимых данных
    result = CheckArgs.check_args_add_photo_clothes(photo_base64, user_name, category, subcategory,
                                                    sub_subcategory)
    if result["status"] == "error":
        return jsonify(result), 400

    id_user = ManageQuery.get_id_user(user_name)
    if not id_user:
        return jsonify({
            "error": f"Пользователь с именем {user_name} не найден"
        }), 400

    try:
        # Проверка уникальности
        decode_image = Base64Utils.decode_base64_in_image(photo_base64)
        file_hash = calculate_hash(decode_image)
        if not ManageQuery.is_photo_clothes_unique(file_hash, id_user):
            return jsonify({"error": "Photo already exists"}), 400

        processed_path, file_hash, error_response, status_code = clothes_bl.process_photo_common(
            photo_base64,
            Base64Utils.writing_file_clothes,
            clothes_bl.remove_background_clothes,
            config.PROCESSED_FOLDER_CLOTHES
        )
        if error_response:
            return error_response, status_code

        # Сохранение в БД
        encode_image, error_response, status_code = clothes_bl.save_photo_to_db(
            processed_path,
            file_hash,
            user_name,
            category,
            subcategory,
            sub_subcategory,
            ManageQuery.add_hash_photos_clothes
        )
        if error_response:
            return error_response, status_code

        return jsonify({
            "status": "success",
            "message": "Фон успешно удален",
            # "image_base64": f"data:image/png;base64,{encode_image}"
        })
    except Exception as error:
        return jsonify({"error": f"Ошибка обработки запроса: {str(error)}"}), 500


@add_photos.route("/catalog/add_photos", methods=["POST"])
def add_photos_in_catalog():
    """
    Добавление фото в каталог администратором
    :return: JSON с результатом операции
    """
    # Получаем данные из JSON
    photo_base64, user_name, category, subcategory, sub_subcategory = clothes_bl.get_data_from_json_add_photos(
        request.json)

    # Проверка необходимых данных
    result = CheckArgs.check_args_add_photo_clothes(photo_base64, user_name, category, subcategory,
                                                    sub_subcategory)
    if result["status"] == "error":
        return jsonify(result), 400

    is_admin = CheckArgs.check_is_admin(user_name)
    if is_admin["status"] == "error":
        return jsonify(is_admin), 403

    id_user = ManageQuery.get_id_user(user_name)
    if not id_user:
        return jsonify({
            "error": f"Пользователь с именем {user_name} не найден"
        }), 400

    try:
        # Проверка уникальности
        decode_image = Base64Utils.decode_base64_in_image(photo_base64)
        file_hash = calculate_hash(decode_image)
        if not ManageQuery.is_photo_catalog_unique(file_hash, id_user):
            return jsonify({"error": "Photo already exists"}), 400

        # Обработка фото
        processed_path, file_hash, error_response, status_code = clothes_bl.process_photo_common(
            photo_base64,
            Base64Utils.writing_file_clothes_catalog,
            clothes_bl.remove_background_clothes_catalog,
            config.PROCESSED_FOLDER_CATALOG
        )
        if error_response:
            return error_response, status_code

        # Сохранение в БД
        encode_image, error_response, status_code = clothes_bl.save_photo_to_db(
            processed_path,
            file_hash,
            user_name,
            category,
            subcategory,
            sub_subcategory,
            ManageQuery.add_hash_photos_clothes_catalog
        )
        if error_response:
            return error_response, status_code

        return jsonify({
            "status": "success",
            "message": "Фон успешно удален",
            # "image_base64": f"data:image/png;base64,{encode_image}"
        })
    except Exception as error:
        return jsonify({"error": f"Ошибка обработки запроса: {str(error)}"}), 500
