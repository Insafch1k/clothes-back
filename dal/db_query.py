import os
from datetime import datetime

import psycopg2
from werkzeug.utils import secure_filename

from dal.db_connection import DBConnection
from psycopg2 import Error
import logging
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные окружения из .env файла


class ManageQuery:
    @staticmethod
    def _execute_query(query, params=None, fetch=False):  # Метод для выполнения SQL запросов
        with DBConnection.get_con() as con:
            with con.cursor() as cursor:
                try:
                    if params and isinstance(params,
                                             list):  # Если параметры переданы как список, используем executemany
                        cursor.executemany(query, params)
                    else:  # Иначе используем execute
                        if not isinstance(params, tuple):  # Если params не кортеж, преобразуем его в кортеж
                            params = (params,)
                        cursor.execute(query, params or ())

                    if fetch:
                        result = cursor.fetchall()
                        return result  # Иначе вернуть весь результат

                    con.commit()
                except Error as e:
                    # logging.error(f"Error executing query: {str(e)}")
                    con.rollback()
                    raise
                return None  # Явный возврат None, если fetch=False

    @staticmethod
    def get_id_user(user_name):  # Получает id_user по user_name
        try:
            query = """
                    SELECT id_user FROM users
                    WHERE name = %s
            """
            result = ManageQuery._execute_query(query, user_name, True)
            if not result:
                result = None
            else:
                result = result[0][0]
            return result
        except Error as e:
            logging.error(f"Error get id user {str(e)}")
            return None

    @staticmethod
    def get_id_category_photos(category):  # Получает id_category фото человека по названию категории
        try:
            query = """
                    SELECT id_category FROM category_photos
                    WHERE category = %s
            """
            result = ManageQuery._execute_query(query, category, True)
            if not result:
                result = None
            else:
                result = result[0][0]
            return result
        except Error as e:
            logging.error(f"Error get id category_photos {str(e)}")
            return None

    @staticmethod
    def photo_users_not_exist(photo_path,
                              user_name):  # Проверяет, существует ли путь к фото человека в базе данных у этого человека
        try:
            id_user = ManageQuery.get_id_user(user_name)
            query = """
                    SELECT id_photo FROM photo_users
                    WHERE photo_path = %s AND id_user = %s
            """
            result = ManageQuery._execute_query(query, (photo_path, id_user), True)
            ret = True
            if result:
                ret = False
            return ret
        except Error as e:
            logging.error(f"Error photo_background not exist {str(e)}")
            return None

    @staticmethod
    def check_args_add_photo(id_user, id_category, user_name, category, photo_path):
        ret = True
        if id_user is None:
            logging.error(f"User '{user_name}' not found")
            ret = False
        if id_category is None:
            logging.error(f"Category '{category}' not found")
            ret = False
        if photo_path == "":
            logging.error("Photo path is empty")
        return ret

    @staticmethod
    def add_photo_user(user_name, photo_path, category="full",
                       is_cut=True):  # Добавляет путь к фото человека в базу данных
        ret = False

        if ManageQuery.photo_users_not_exist(photo_path,
                                             user_name):  # Проверяет, существует ли путь фото человека в базе данных у этого человека
            try:
                id_user = ManageQuery.get_id_user(user_name)
                id_category = ManageQuery.get_id_category_photos(category)
                if ManageQuery.check_args_add_photo(id_user, id_category, user_name, category, photo_path):
                    query = """
                            INSERT INTO photo_users (id_user, photo_path, id_category, is_cut)
                            VALUES (%s, %s, %s, %s)
                    """
                    ManageQuery._execute_query(query, (id_user, photo_path, id_category, is_cut))
                    logging.info(f"Photo path added successfully for user {user_name}")
                    ret = True
                else:
                    logging.error("Invalid user id, category id or photo_background path is empty")
            except Error as e:
                logging.error(f"Error add photo_background user {str(e)}")
        else:
            logging.warning("Это фото уже есть в базе данных у этого человека")
        return ret

    @staticmethod
    def delete_photo_user(photo_path):  # Удаляет путь фото человека из базы данных
        ret = False
        if photo_path:
            try:
                query = """
                        DELETE FROM photo_users
                        WHERE photo_path = %s
                """
                ManageQuery._execute_query(query, photo_path)
                ret = True
            except Error as e:
                logging.error(f"Error delete photo_path user: {str(e)}")
        else:
            logging.error("Photo path is empty")
        return ret

    @staticmethod
    def photo_clothes_not_exist(photo_path,
                                user_name):  # Проверяет, существует ли путь фото в базе данных у этого человека
        try:
            id_user = ManageQuery.get_id_user(user_name)
            query = """
                    SELECT id_clothes FROM photo_clothes
                    WHERE photo_path = %s AND id_user = %s
            """
            result = ManageQuery._execute_query(query, (photo_path, id_user), True)
            ret = True
            if result:
                ret = False
            return ret
        except Error as e:
            logging.error(f"Error photo_background not exist {str(e)}")
            return None

    @staticmethod
    def get_id_category_clothes(category):  # Получает id_category фото одежды по названию категории
        try:
            query = """
                    SELECT id_category FROM category_clothes
                    WHERE category = %s
            """
            result = ManageQuery._execute_query(query, category, True)
            if not result:
                result = None
            else:
                result = result[0][0]
            return result
        except Error as e:
            logging.error(f"Error get id category_photos {str(e)}")
            return None

    @staticmethod
    def add_photo_clothes(user_name, photo_path, category, is_cut=True):  # Добавляет фото одежды в базу данных
        ret = False

        if ManageQuery.photo_clothes_not_exist(photo_path,
                                               user_name):  # Проверяет, существует ли путь к фото одежды в базе данных у этого человека
            try:
                id_user = ManageQuery.get_id_user(user_name)
                id_category = ManageQuery.get_id_category_clothes(category)
                # binary_photo = ManageQuery.photo_in_binary(photo_background)
                if ManageQuery.check_args_add_photo(id_user, id_category, user_name, category, photo_path):
                    query = """
                            INSERT INTO photo_clothes (id_user, photo_path, id_category, is_cut)
                            VALUES (%s, %s, %s, %s)
                    """
                    ManageQuery._execute_query(query, (id_user, photo_path, id_category, is_cut))
                    logging.info(f"Photo clothes added successfully for user {user_name}")
                    ret = True
                else:
                    logging.error("Invalid user id, category id, or photo_path")
            except Error as e:
                logging.error(f"Error add photo_background user {str(e)}")
        else:
            logging.warning("Это фото одежды уже есть в базе данных у этого человека")
        return ret

    @staticmethod
    def delete_photo_clothes(photo_path):  # Удаляет фото одежды из базы данных
        ret = False
        if photo_path:

            try:
                query = """
                        DELETE FROM photo_clothes
                        WHERE photo_path = %s
                """
                ManageQuery._execute_query(query, photo_path)
                ret = True
            except Error as e:
                logging.error(f"Error delete photo_path clothes: {str(e)}")
        else:
            logging.error("Photo path is empty")
        return ret
