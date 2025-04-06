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
    photo_base64, user_name, category, subcategory, sub_subcategory = clothes_bl.get_data_from_json(request.json)

    # Проверка необходимых данных
    result = CheckArgs.check_args_add_photo_clothes(photo_base64, user_name, category, subcategory,
                                                    sub_subcategory)
    if result["status"] == "error":
        return jsonify(result), 400

    try:
        # Проверка уникальности
        decode_image = Base64Utils.decode_base64_in_image(photo_base64)
        file_hash = calculate_hash(decode_image)
        if not ManageQuery.is_photo_clothes_unique(file_hash):
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

        # # Декодируем base64
        # decode_image = Base64Utils.decode_base64_in_image(photo_base64)
        #
        # # Проверяем уникальность по хэшу
        # file_hash = calculate_hash(decode_image)
        # if not ManageQuery.is_photo_clothes_unique(file_hash):
        #     return jsonify({"error": "Photo already exists"}), 400
        #
        # # Генерируем уникальное имя файла.
        # # Декодируем base64 и сохраняем изображение
        # try:
        #     input_path = Base64Utils.writing_file_clothes(photo_base64)
        # except Exception as e:
        #     return jsonify({"error": f"Failed to save image: {str(e)}"}), 500
        #
        # # Удаляем фон
        # output_filename = clothes_bl.remove_background_clothes(input_path)
        #
        # # Удаляем необработанное фото
        # if os.path.exists(input_path):
        #     os.remove(input_path)
        #
        # if output_filename:
        #     # Путь к обработанному изображению
        #     processed_path = os.path.join(config.PROCESSED_FOLDER, output_filename)
        #
        #     # Сохраняем информацию о фотографии пользователя
        #     try:
        #         id_clothes = ManageQuery.add_photo_clothes(user_name=user_name, photo_path=processed_path,
        #                                                    category=category, subcategory=subcategory,
        #                                                    sub_subcategory=sub_subcategory, is_cut=True)
        #         if id_clothes:
        #             ManageQuery.add_hash_photos_clothes(id_clothes, file_hash)
        #             encode_image = Base64Utils.encode_to_base64(processed_path)
        #
        #             return jsonify({
        #                 "status": "success",
        #                 "message": "Фон успешно удален",
        #                 "image_base64": f"data:image/png;base64,{encode_image}"
        #             })
        #         else:
        #             return jsonify({"error": "Ошибка сохранения данных в БД"}), 500
        #     except Exception as db_error:
        #         return jsonify({"error": f"Ошибка при работе с БД: {str(db_error)}"}), 500
        # else:
        #     return jsonify({"error": "Ошибка обработки изображения"}), 500
        return jsonify({
            "status": "success",
            "message": "Фон успешно удален",
            "image_base64": f"data:image/png;base64,{encode_image}"
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
    photo_base64, user_name, category, subcategory, sub_subcategory = clothes_bl.get_data_from_json(request.json)

    # Проверка необходимых данных
    result = CheckArgs.check_args_add_photo_clothes(photo_base64, user_name, category, subcategory,
                                                    sub_subcategory)
    if result["status"] == "error":
        return jsonify(result), 400

    is_admin = CheckArgs.check_is_admin(user_name)
    if is_admin["status"] == "error":
        return jsonify(is_admin), 403

    try:

        # # Декодируем base64
        # decode_image = Base64Utils.decode_base64_in_image(photo_base64)
        #
        # # Проверяем уникальность по хэшу
        # file_hash = calculate_hash(decode_image)
        # if not ManageQuery.is_photo_catalog_unique(file_hash):
        #     return jsonify({"error": "Photo already exists"}), 400
        #
        # # Генерируем уникальное имя файла.
        # # Декодируем base64 и сохраняем изображение
        # try:
        #     input_path = Base64Utils.writing_file_clothes_catalog(photo_base64)
        # except Exception as e:
        #     return jsonify({"error": f"Failed to save image catalog: {str(e)}"}), 500
        #
        # # Удаляем фон
        # output_filename = clothes_bl.remove_background_clothes_catalog(input_path)
        #
        # # Удаляем необработанное фото
        # if os.path.exists(input_path):
        #     os.remove(input_path)
        #
        # if output_filename:
        #     # Путь к обработанному изображению
        #     processed_path = os.path.join(config.PROCESSED_FOLDER_CATALOG, output_filename)
        #
        #     # Сохраняем информацию о фотографии пользователя
        #     try:
        #         id_clothes = ManageQuery.add_photo_clothes(user_name=user_name, photo_path=processed_path,
        #                                                    category=category, subcategory=subcategory,
        #                                                    sub_subcategory=sub_subcategory, is_cut=True)
        #         if id_clothes:
        #             ManageQuery.add_hash_photos_clothes_catalog(id_clothes, file_hash)
        #             encode_image = Base64Utils.encode_to_base64(processed_path)
        #
        #             return jsonify({
        #                 "status": "success",
        #                 "message": "Фон успешно удален",
        #                 "image_base64": f"data:image/png;base64,{encode_image}"
        #             })
        #         else:
        #             return jsonify({"error": "Ошибка сохранения данных в БД"}), 500
        #     except Exception as db_error:
        #         return jsonify({"error": f"Ошибка при работе с БД: {str(db_error)}"}), 500
        # else:
        #     return jsonify({"error": "Ошибка обработки изображения"}), 500
        # Проверка уникальности
        decode_image = Base64Utils.decode_base64_in_image(photo_base64)
        file_hash = calculate_hash(decode_image)
        if not ManageQuery.is_photo_catalog_unique(file_hash):
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
            "image_base64": f"data:image/png;base64,{encode_image}"
        })
    except Exception as error:
        return jsonify({"error": f"Ошибка обработки запроса: {str(error)}"}), 500
