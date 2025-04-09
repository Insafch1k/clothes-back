import logging

from flask import jsonify
import dal.db_query
import os


class CheckArgs:
    @staticmethod
    def check_args_add_photo_clothes_db(id_user, id_category, id_subcategory, id_sub_subcategory, user_name, category,
                                        subcategory,
                                        sub_subcategory,
                                        photo_path):
        ret = True
        if id_user is None:
            logging.error(f"User '{user_name}' not found")
            ret = False
        if id_category is None:
            logging.error(f"Category '{category}' not found")
            ret = False
        if id_subcategory is None:
            logging.error(f"Subcategory '{subcategory}' not found")
            ret = False
        if id_sub_subcategory is None:
            logging.error(f"Sub_subcategory '{sub_subcategory}' not found")
            ret = False
        if photo_path == "":
            logging.error("Photo path is empty")
            ret = False
        return ret

    @staticmethod
    def check_args_add_photo_person(id_user, id_category, user_name, category, photo_path):
        ret = True
        if id_user is None:
            logging.error(f"User '{user_name}' not found")
            ret = False
        if id_category is None:
            logging.error(f"Category '{category}' not found")
            ret = False
        if photo_path == "":
            logging.error("Photo path is empty")
            ret = False
        return ret

    # @staticmethod
    # def check_args_add_photo_clothes():

    @staticmethod
    def check_args_add_photo_clothes(photo_base64, user_name, category, subcategory, sub_subcategory):
        ret = {
            "status": "success"
        }
        if not user_name:
            ret = {
                "status": "error",
                "error": "Отсутствует параметр user_name"
            }
        if not photo_base64:
            ret = {
                "status": "error",
                "error": "Отсутствует параметр photo (base64)"
            }
        if not category:
            ret = {
                "status": "error",
                "error": "Отсутствует параметр category"
            }
        if not subcategory:
            return {
                "status": "error",
                "error": "Отсутствует параметр subcategory"
            }
        if not sub_subcategory:
            return {
                "status": "error",
                "error": "Отсутствует параметр sub_subcategory"
            }
        # is_admin = CheckArgs.check_is_admin(user_name)
        # if is_admin["status"] == "error":
        #     ret = is_admin
        return ret

    @staticmethod
    def check_args_recovery_photos(id, user_name):
        ret = {
            "status": "success"
        }
        if not id:
            ret = {
                "status": "error",
                "error": "Отсутствует параметр id"
            }
        if not user_name:
            ret = {
                "status": "error",
                "error": "Отсутствует параметр user_name"
            }
        return ret

    @staticmethod
    def check_args_recovery_photos_wardrobe(id_clothes, user_name):
        # Проверка необходимых данных
        result = CheckArgs.check_args_recovery_photos(id_clothes, user_name)
        if result["status"] == "error":
            return result

        id_user = dal.db_query.ManageQuery.get_id_user(user_name)
        if id_user is None:
            return {
                "status": "error",
                "error": f"user_name '{user_name}' не найден"
            }

        if not dal.db_query.ManageQuery.is_photo_clothes_deleted(id_clothes):
            return {
                "status": "error",
                "error": f"Фото одежды с id {id_clothes} не удалено"
            }
        return result

    @staticmethod
    def check_args_recovery_photos_human(id_photo, user_name):
        # Проверка необходимых данных
        result = CheckArgs.check_args_recovery_photos(id_photo, user_name)
        if result["status"] == "error":
            return result

        id_user = dal.db_query.ManageQuery.get_id_user(user_name)
        if id_user is None:
            return {
                "status": "error",
                "error": f"user_name '{user_name}' не найден"
            }

        if not dal.db_query.ManageQuery.is_photo_user_deleted(id_photo):
            return {
                "status": "error",
                "error": f"Фото человека {user_name} с id_фото {id_photo} не удалено"
            }
        return result

    @staticmethod
    def check_is_admin(user_name):
        if str(dal.db_query.ManageQuery.get_id_user(user_name)) not in os.getenv('ADMIN_LIST'):
            return {
                "status": "error",
                "error": f"Пользователь {user_name} не является администратором"
            }
        else:
            return {
                "status": "success",
                "message": f"Пользователь {user_name} является администратором"
            }
