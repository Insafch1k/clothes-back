from rembg import remove
from PIL import Image
import os
import uuid
import config
from bl.utils.create_folders import create_folders_for_background
from flask import jsonify
from ..utils.base64_utils import Base64Utils
from dal.db_query import ManageQuery
from ..utils.hash import calculate_hash


create_folders_for_background()


def remove_background(input_path):
    try:
        input_image = Image.open(input_path)
        output_image = remove(input_image)

        output_filename = f"{uuid.uuid4().hex}.png"
        output_path = os.path.join(config.PROCESSED_FOLDER_BACKGROUND, output_filename)

        output_image.save(output_path)
        return output_filename
    except Exception as error:
        print(f"Ошибка обработки изображения: {error}")
        return None


def get_data_from_json_recovery_photos_human(data):
    id_photo = data.get("id_photo")
    user_name = data.get("user_name")

    return id_photo, user_name


def process_photo_common(photo_base64, writing_file_func, remove_background_func, processed_folder):
    """
    Общая функция для обработки фото
    :param photo_base64: фото в формате base64
    :param writing_file_func: функция для сохранения файла
    :param remove_background_func: функция для удаления фона
    :param processed_folder: папка для обработанных фото
    :return: кортеж (processed_path, file_hash, error_response, status_code)
    """
    processed_path = None
    json = None
    status_code = None
    try:
        # Вычисляем хэш
        decode_image = Base64Utils.decode_base64_in_image(photo_base64)
        file_hash = calculate_hash(decode_image)

        # Декодируем base64 и сохраняем изображение
        input_path = writing_file_func(photo_base64)

        # Удаляем фон
        output_filename = remove_background_func(input_path)

        # Удаляем необработанное изображение
        if os.path.exists(input_path):
            os.remove(input_path)

        if not output_filename:
            file_hash = None
            json = jsonify({"error": "Image processing error"})
            status_code = 500
        else:
            processed_path = os.path.join(processed_folder, output_filename)
        return processed_path, file_hash, json, status_code

    except Exception as e:
        return None, None, jsonify({"error": f"Error while processing photo: {str(e)}"}), 500


def save_photo_to_db(processed_path, file_hash, id_user, add_hash_func):
    """
    Сохраняет фото в базу данных
    :param processed_path: путь к обработанному фото
    :param file_hash: хэш фото
    :param id_user: ID пользователя
    :param add_hash_func: функция для добавления хэша
    :return: кортеж (encode_image, error_response, status_code)
    """
    try:
        # Сохраняем информацию о фотографии пользователя
        id_photo = ManageQuery.add_photo_user(id_user=id_user, photo_path=processed_path, category="full",
                                              is_cut=True)

        if not id_photo:
            return None, jsonify({"error": "Error saving data to DB"}), 500

        # Добавляем хэш
        add_hash_func(id_photo, file_hash)

        # Кодируем фото в base64
        encode_image = Base64Utils.encode_to_base64(processed_path)

        return encode_image, None, None

    except Exception as e:
        return None, jsonify({"error": f"Error saving data to DB: {str(e)}"}), 500