import os
from datetime import datetime

import psycopg2
from werkzeug.utils import secure_filename
# comment
from dal.db_connection import DBConnection
from psycopg2 import Error
import logging
from dotenv import load_dotenv
from bl.utils.check_args import CheckArgs

load_dotenv()  # Загружаем переменные окружения из .env файла


class ManageQuery:
    @staticmethod
    def _execute_query(query, params=None, fetch=False, fetch_insert=False):  # Метод для выполнения SQL запросов
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

                    # Обработка результатов
                    result = None
                    if fetch:
                        result = cursor.fetchall()
                    elif fetch_insert:
                        result = cursor.fetchone()

                    con.commit()  # Фиксируем изменения В ЛЮБОМ СЛУЧАЕ
                    return result
                except Error as e:
                    # logging.error(f"Error executing query: {str(e)}")
                    con.rollback()
                    raise

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
    def add_photo_user(user_name, photo_path, category="full",
                       is_cut=True):  # Добавляет путь к фото человека в базу данных
        ret = False

        try:
            id_user = ManageQuery.get_id_user(user_name)
            id_category = ManageQuery.get_id_category_photos(category)
            if CheckArgs.check_args_add_photo_person(id_user, id_category, user_name, category, photo_path):
                query = """
                        INSERT INTO photo_users (id_user, photo_path, id_category, is_cut)
                        VALUES (%s, %s, %s, %s) returning id_photo
                """
                id_clothes = ManageQuery._execute_query(query, (id_user, photo_path, id_category, is_cut),
                                                        fetch_insert=True)
                logging.info(f"Photo users added successfully for user {user_name}")
                ret = id_clothes
            else:
                logging.error("Invalid user id, category id or photo path is empty")
        except Error as e:
            logging.error(f"Error add photo user {str(e)}")
        return ret

    # @staticmethod
    # def delete_photo_user(photo_path):  # Удаляет путь фото человека из базы данных
    #     ret = False
    #     if photo_path:
    #         try:
    #             query = """
    #                     DELETE FROM photo_users
    #                     WHERE photo_path = %s
    #             """
    #             ManageQuery._execute_query(query, photo_path)
    #             ret = True
    #         except Error as e:
    #             logging.error(f"Error delete photo_path user: {str(e)}")
    #     else:
    #         logging.error("Photo path is empty")
    #     return ret

    @staticmethod
    def delete_photo_user(id_photo):  # Мягкое удаление фото пользователя из базы данных
        if id_photo:
            try:
                query = """
                        UPDATE photo_users
                        SET deleted_at = CURRENT_TIMESTAMP
                        WHERE id_photo = %s
                        RETURNING id_photo
                """
                result = ManageQuery._execute_query(query, id_photo, fetch_insert=True)
                if not result:
                    result = None
                return result
            except Error as e:
                logging.error(f"Error delete photo user: {str(e)}")
        else:
            logging.error("id photo is empty")
            return False

    @staticmethod
    def is_photo_clothes_unique(file_hash):
        """Проверяет, есть ли уже такое фото одежды у пользователя"""
        try:
            query = """
                SELECT id_clothes FROM hash_photos_clothes 
                WHERE hash = %s
                LIMIT 1
            """
            result = ManageQuery._execute_query(query, file_hash, True)
            ret = True
            if result:
                ret = False
            return ret
        except Error as e:
            logging.error(f"Error in is_photo_clothes_unique {str(e)}")
            return None

    @staticmethod
    def is_photo_users_unique(file_hash):
        """Проверяет, есть ли уже такое фото у пользователя"""
        try:
            query = """
                SELECT id_photo FROM hash_photos_users 
                WHERE hash = %s
                LIMIT 1
            """
            result = ManageQuery._execute_query(query, file_hash, True)
            ret = True
            if result:
                ret = False
            return ret
        except Error as e:
            logging.error(f"Error in is_photo_users_unique {str(e)}")
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
            logging.error(f"Error get id category_clothes {str(e)}")
            return None

    @staticmethod
    def get_id_sub_subcategory_clothes(
            sub_subcategory):  # Получает id_sub_subcategory фото одежды по названию под-подкатегории
        try:
            query = """
                    SELECT id_sub_subcategory FROM sub_subcategory_clothes
                    WHERE sub_subcategory = %s
            """
            result = ManageQuery._execute_query(query, sub_subcategory, True)
            if not result:
                result = None
            else:
                result = result[0][0]
            return result
        except Error as e:
            logging.error(f"Error get id sub_subcategory_clothes {str(e)}")
            return None

    @staticmethod
    def get_id_subcategory_clothes(
            subcategory):  # Получает id_subcategory фото одежды по названию подкатегории
        try:
            query = """
                    SELECT id_subcategory FROM subcategory_clothes
                    WHERE subcategory = %s
            """
            result = ManageQuery._execute_query(query, subcategory, True)
            if not result:
                result = None
            else:
                result = result[0][0]
            return result
        except Error as e:
            logging.error(f"Error get id subcategory_clothes {str(e)}")
            return None

    @staticmethod
    def get_clothes_from_wardrobe(id_user, id_category,
                                  id_sub_subcategory):  # Получает id_subcategory, id_category, id_sub_subcategory фото одежды по названию подкатегории
        try:
            query = """
                    SELECT photo_path FROM photo_clothes
                    WHERE id_user = %s AND id_category = %s AND id_sub_subcategory = %s
            """
            result = ManageQuery._execute_query(query, (id_user, id_category, id_sub_subcategory), True)
            if not result:
                result = None
            else:
                for i in range(len(result)):
                    result[i] = result[i][0]
            return result
        except Error as e:
            logging.error(f"Error get id subcategory_clothes {str(e)}")
            return None

    @staticmethod
    def get_clothes_from_catalog(id_category, id_sub_subcategory):
        """
        Возвращает список одежды из каталога по указанной категории и подподкатегории.
        """
        try:
            query = """
                SELECT photo_path
                FROM photo_clothes
                WHERE id_category = %s AND id_sub_subcategory = %s
            """
            result = ManageQuery._execute_query(query, (id_category, id_sub_subcategory), True)
            return result
        except  Error as e:
            logging.error(f"Error get id subcategory_clothes {str(e)}")
            return None

    @staticmethod
    def add_hash_photos_clothes(id_clothes, hash):
        ret = False

        try:
            query = """
                    INSERT INTO hash_photos_clothes(id_clothes, hash)
                    VALUES (%s, %s)
            """
            ManageQuery._execute_query(query, (id_clothes, hash))
            ret = True
        except Error as e:
            logging.error(f"Error add_hash_photos_clothes {str(e)}")
        return ret

    @staticmethod
    def add_hash_photos_users(id_photo, hash):
        ret = False

        try:
            query = """
                    INSERT INTO hash_photos_users(id_photo, hash)
                    VALUES (%s, %s)
            """
            ManageQuery._execute_query(query, (id_photo, hash))
            ret = True
        except Error as e:
            logging.error(f"Error add_hash_photos_users {str(e)}")
        return ret

    @staticmethod
    def add_photo_clothes(user_name, photo_path, category, subcategory, sub_subcategory,
                          is_cut=True):  # Добавляет фото одежды в базу данных
        ret = False

        try:
            id_user = ManageQuery.get_id_user(user_name)
            id_category = ManageQuery.get_id_category_clothes(category)
            id_subcategory = ManageQuery.get_id_subcategory_clothes(subcategory)
            id_sub_subcategory = ManageQuery.get_id_sub_subcategory_clothes(sub_subcategory)

            if CheckArgs.check_args_add_photo_clothes(id_user, id_category, id_subcategory, id_sub_subcategory,
                                                      user_name,
                                                      category, subcategory,
                                                      sub_subcategory, photo_path):
                query = """
                        INSERT INTO photo_clothes (id_user, photo_path, id_category, id_subcategory, id_sub_subcategory, is_cut)
                        VALUES (%s, %s, %s, %s, %s, %s) returning id_clothes
                """
                id_clothes = ManageQuery._execute_query(query, (
                    id_user, photo_path, id_category, id_subcategory, id_sub_subcategory, is_cut), fetch_insert=True)
                logging.info(f"Photo clothes added successfully for user {user_name}")
                ret = id_clothes
            else:
                logging.error("Invalid user id, subcategory id, or photo_path is empty")
        except Error as e:
            logging.error(f"Error add photo clothes {str(e)}")
        return ret

    @staticmethod
    def delete_photo_clothes(id_clothes):  # Мягкое удаление фото одежды из базы данных
        if not id_clothes:
            logging.error("id clothes is empty")
            return {'status': 'error', 'message': 'ID одежды не указан'}

        try:
            # Проверяем существование записи
            if not ManageQuery.exist_id_clothes(id_clothes):
                return {'status': 'error', 'message': f'Одежда с ID {id_clothes} не найдена'}

            # Проверяем, не удалена ли уже запись
            if ManageQuery.is_clothes_deleted(id_clothes):
                return {'status': 'error', 'message': f'Одежда с ID {id_clothes} уже удалена'}

            # Выполняем мягкое удаление
            query = """
                UPDATE photo_clothes
                SET deleted_at = CURRENT_TIMESTAMP
                WHERE id_clothes = %s
                RETURNING id_clothes
            """
            result = ManageQuery._execute_query(query, id_clothes, fetch_insert=True)

            if result:
                return {'status': 'success', 'id': result[0]}
            return {'status': 'error', 'message': 'Не удалось выполнить удаление'}

        except Error as e:
            logging.error(f"Error delete photo clothes: {str(e)}")
            return {'status': 'error', 'message': f'Ошибка базы данных: {str(e)}'}

    @staticmethod
    def is_clothes_deleted(id_clothes) -> bool:
        """Проверяет, удалена ли уже запись"""
        try:
            query = """
                SELECT id_clothes FROM photo_clothes
                WHERE id_clothes = %s AND deleted_at IS NOT NULL
            """
            result = ManageQuery._execute_query(query, id_clothes, fetch=True)
            return bool(result)
        except Error as e:
            logging.error(f"Error in is_clothes_deleted: {str(e)}")
            return False

    @staticmethod
    def get_user_photos_paginated(id_user, limit=20, offset=0):
        try:
            query = """
                    SELECT id_photo, photo_path
                    FROM photo_users
                    WHERE id_user = %s
                    ORDER BY id_photo DESC
                    LIMIT %s OFFSET %s
                """
            result = ManageQuery._execute_query(query, (id_user, limit, offset), True)
            if not result:
                result = None
            return result
        except Error as e:
            logging.error(f"Error get_user_photos_paginated {str(e)}")

    @staticmethod
    def count_user_photos(id_user):
        try:
            query = "SELECT COUNT(*) FROM photo_users WHERE id_user = %s"
            result = ManageQuery._execute_query(query, id_user, True)
            if not result:
                result = None
            return result[0][0]
        except Error as e:
            logging.error(f"Error count user photos {str(e)}")

    @staticmethod
    def exist_id_clothes(id_clothes):
        try:
            query = """
                    SELECT id_clothes FROM photo_clothes
                    WHERE id_clothes = %s
            """
            result = ManageQuery._execute_query(query, id_clothes, fetch=True)
            if not result:
                result = None
            else:
                result = result[0][0]
            return result
        except Error as e:
            logging.error(f"Error exist id clothes {str(e)}")
