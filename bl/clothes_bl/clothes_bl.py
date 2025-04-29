from flask import jsonify
from rembg import remove
from PIL import Image
import os
import uuid
import logging
import config
from dal.db_query import ManageQuery
from ..utils.base64_utils import Base64Utils
from ..utils.hash import calculate_hash


def remove_background_clothes(input_path):
    """
    Удаляет фон из изображения и сохраняет результат.
    """
    try:
        input_image = Image.open(input_path)
        output_image = remove(input_image)

        output_filename = f"{uuid.uuid4().hex}.png"
        output_path = os.path.join(config.PROCESSED_FOLDER_CLOTHES, output_filename)

        output_image.save(output_path)
        return output_filename
    except Exception as error:
        logging.error(f"Ошибка обработки изображения: {error}")
        return None


def remove_background_clothes_catalog(input_path):
    """
    Удаляет фон из изображения для каталога и сохраняет результат.
    """
    try:
        input_image = Image.open(input_path)
        output_image = remove(input_image)

        output_filename = f"{uuid.uuid4().hex}.png"
        output_path = os.path.join(config.PROCESSED_FOLDER_CATALOG, output_filename)

        output_image.save(output_path)
        return output_filename
    except Exception as error:
        logging.error(f"Ошибка обработки изображения для каталога: {error}")
        return None


# def get_data_from_json(json):
#     data = {
#         "photo_base64": json.get("image"),
#         "user_name": json.get("user_name"),
#         "category": json.get("category"),
#         "subcategory": json.get("subcategory"),
#         "sub_subcategory": json.get("sub_subcategory")
#     }
#     return data

def get_data_from_json_add_photos(data):
    photo_base64 = data.get("image")
    # user_name = data.get("user_name")
    category = data.get("category")
    subcategory = data.get("subcategory")
    sub_subcategory = data.get("sub_subcategory")

    return photo_base64, category, subcategory, sub_subcategory

def get_data_from_json_recovery_photos(data):
    id_clothes = data.get("id_clothes")
    user_name = data.get("user_name")

    return id_clothes, user_name


def process_photo_common(photo_base64, writing_func, remove_bg_func, processed_folder):
    """Общая обработка фото: сохранение, удаление фона, подготовка пути"""
    processed_path = None
    json = None
    status_code = None
    try:
        # Декодируем и проверяем уникальность
        decode_image = Base64Utils.decode_base64_in_image(photo_base64)
        file_hash = calculate_hash(decode_image)

        # Сохраняем временный файл
        input_path = writing_func(photo_base64)

        # Удаляем фон
        output_filename = remove_bg_func(input_path)

        # Удаляем временный файл
        if os.path.exists(input_path):
            os.remove(input_path)

        if not output_filename:
            file_hash = None
            json = jsonify({"error": "Ошибка обработки изображения"})
            status_code = 500
            # return None, None, jsonify({"error": "Ошибка обработки изображения"}), 500
        else:
            processed_path = os.path.join(processed_folder, output_filename)
        return processed_path, file_hash, json, status_code

    except Exception as e:
        return None, None, jsonify({"error": f"Ошибка обработки: {str(e)}"}), 500


def save_photo_to_db(processed_path, file_hash, id_category, id_subcategory, id_sub_subcategory, id_user,
                     add_hash_func):
    """
    Сохранение информации о фото в БД
    """
    try:
        id_clothes = ManageQuery.add_photo_clothes(
            photo_path=processed_path,
            id_category=id_category,
            id_subcategory=id_subcategory,
            id_sub_subcategory=id_sub_subcategory,
            id_user=id_user,
            is_cut=True
        )

        if not id_clothes:
            return None, jsonify({"error": "Ошибка сохранения данных в БД"}), 500

        add_hash_func(id_clothes, file_hash)
        encode_image = Base64Utils.encode_to_base64(processed_path)

        return encode_image, None, None

    except Exception as e:
        return None, jsonify({"error": f"Ошибка при работе с БД: {str(e)}"}), 500


def validate_and_get_id(source, id_user, category, subcategory, sub_subcategory):
    try:
        if source == "wardrobe":
            if id_user is None:
                return {"error": f"User not found"}, 404

        id_category = ManageQuery.get_id_category_clothes(category)
        if id_category is None:
            return {"error": f"Категория '{category}' не найдена"}, 404

        id_subcategory = ManageQuery.get_id_subcategory_clothes(subcategory)
        if id_subcategory is None:
            return {"error": f"Подкатегория '{category}' не найдена"}, 404

        id_sub_subcategory = ManageQuery.get_id_sub_subcategory_clothes(sub_subcategory)
        if id_sub_subcategory is None:
            return {"error": f"Подподкатегория '{sub_subcategory}' не найдена"}, 404

        return {
            "id_user": id_user,
            "id_category": id_category,
            "id_subcategory": id_subcategory,
            "id_sub_subcategory": id_sub_subcategory
        }, 200
    except Exception as e:
        return {"error": f"Ошибка в валидации: {str(e)}"}, 500


def fetch_clothes(source, id_user, id_category, id_subcategory, id_sub_subcategory, limit, offset):
    try:
        if source == "wardrobe":
            clothes = ManageQuery.get_clothes_from_wardrobe_paginated(
                id_user=id_user, id_category=id_category, id_subcategory=id_subcategory,
                id_sub_subcategory=id_sub_subcategory,
                limit=limit, offset=offset
            )
            total = ManageQuery.count_clothes_in_wardrobe(id_user, id_category, id_subcategory, id_sub_subcategory)
            # total = 1
        elif source == "catalog":
            clothes = ManageQuery.get_clothes_from_catalog_paginated(
                id_category=id_category, id_subcategory=id_subcategory, id_sub_subcategory=id_sub_subcategory,
                limit=limit, offset=offset
            )
            total = ManageQuery.count_clothes_in_catalog(id_category, id_subcategory, id_sub_subcategory)
            # total = 1
        else:
            logging.error(f"Invalid source: {source}")
            raise ValueError("Invalid source")

        return clothes, total
    except Exception as e:
        logging.exception(f"Ошибка в fetch_clothes {str(e)}")
        raise


def get_clothes_by_type(source, id_user, category, subcategory, sub_subcategory, page, limit):
    try:
        offset = (page - 1) * limit

        id_result, status_code = validate_and_get_id(source, id_user, category, subcategory, sub_subcategory)

        if status_code != 200:
            return id_result, status_code

        id_user = id_result.get("id_user")
        id_category = id_result.get("id_category")
        id_subcategory = id_result.get("id_subcategory")
        id_sub_subcategory = id_result.get("id_sub_subcategory")

        clothes_list, total_items = fetch_clothes(
            source, id_user, id_category, id_subcategory, id_sub_subcategory, limit, offset
        )

        if not clothes_list:
            return jsonify(
                {
                    "error": f"Одежда в категории '{category}', подкатегории '{subcategory}' и подподкатегории '{sub_subcategory}' не найдена"}), 404

        clothes_list = [
            {
                "id_clothes": item["id_clothes"],
                "photo": Base64Utils.encode_to_base64(item["photo_path"])
            }
            for item in clothes_list
        ]

        return jsonify({
            "page": page,
            "limit": limit,
            "total_items": total_items,
            "clothes": clothes_list
        }), 200

    except Exception as error:
        return jsonify({"error": f"Ошибка получения одежды: {str(error)}"}), 500
