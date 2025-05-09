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
    def get_id_user_by_id(id_user):
        """"
        Проверяет существование пользователя по его ID
        """
        try:
            query = """
                SELECT id_user FROM users
                WHERE id_user = %s
            """
            result = ManageQuery._execute_query(query, id_user, fetch=True)
            if result:
                return result[0][0]
            return None
        except Error as e:
            logging.error(f"Error get_id_user_by_id: {str(e)}")
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
    def add_photo_user(id_user, photo_path, category="full",
                       is_cut=True):  # Добавляет путь к фото человека в базу данных
        ret = False

        try:
            id_category = ManageQuery.get_id_category_photos(category)
            if CheckArgs.check_args_add_photo_person(id_user, id_category, category, photo_path):
                query = """
                        INSERT INTO photo_users (id_user, photo_path, id_category, is_cut)
                        VALUES (%s, %s, %s, %s) returning id_photo
                """
                id_clothes = ManageQuery._execute_query(query, (id_user, photo_path, id_category, is_cut),
                                                        fetch_insert=True)
                logging.info(f"Photo users added successfully for user with id {id_user}")
                ret = id_clothes
            else:
                logging.error("Invalid user id, category id or photo path is empty")
        except Error as e:
            logging.error(f"Error add photo user {str(e)}")
        return ret

    @staticmethod
    def delete_hash_photos_users(id_photo):
        try:
            query = """
                    DELETE FROM hash_photos_users
                    WHERE id_photo = %s RETURNING id_photo
            """
            result = ManageQuery._execute_query(query, id_photo, fetch_insert=True)

            if not result:
                result = None
            return result
        except Error as e:
            logging.error(f"Error delete hash photos clothes {str(e)}")
            return False

    @staticmethod
    def delete_photo_user(id_photo, id_user):  # Мягкое удаление фото пользователя из базы данных
        if not id_photo:
            logging.error("id photo is empty")
            return {'status': 'error', 'message': 'User photo ID not specified'}

        try:
            # Проверяем существование записи
            if not ManageQuery.exist_id_photo_user(id_photo):
                return {'status': 'error', 'message': f'Photos with ID {id_photo} not found'}

            # Проверяем, не удалена ли уже запись
            if ManageQuery.is_photo_user_deleted(id_photo):
                return {'status': 'error', 'message': f'Photo with ID {id_photo} has already been removed'}

            # Проверяем принадлежность фото пользователю
            if not ManageQuery.is_photo_belongs_to_user(id_photo, id_user):
                return {'status': 'error', 'message': f'Photo with ID {id_photo} does not belong to the user'}

            # Выполняем мягкое удаление
            query = """
                    UPDATE photo_users
                    SET deleted_at = CURRENT_TIMESTAMP
                    WHERE id_photo = %s AND id_user = %s
                    RETURNING id_photo
            """
            result = ManageQuery._execute_query(query, (id_photo, id_user), fetch_insert=True)

            # if result and ManageQuery.delete_hash_photos_users(id_photo):
            if result:
                return {'status': 'success', 'id': result[0]}
            return {'status': 'error', 'message': 'Unable to perform deletion'}

        except Error as e:
            logging.error(f"Error delete photo user: {str(e)}")
            return {'status': 'error', 'message': f'Database error: {str(e)}'}

    @staticmethod
    def is_photo_user_deleted(id_photo) -> bool:
        """
        Проверяет, удалено ли фото пользователя
        """
        try:
            query = """
                SELECT id_photo FROM photo_users
                WHERE id_photo = %s AND deleted_at IS NOT NULL
            """
            result = ManageQuery._execute_query(query, id_photo, fetch=True)
            return bool(result)
        except Error as e:
            logging.error(f"Error in is photo user deleted: {str(e)}")
            return False

    @staticmethod
    def is_photo_clothes_deleted(id_clothes) -> bool:
        """
        Проверяет, удалено ли фото одежды
        """
        try:
            query = """
                SELECT id_clothes FROM photo_clothes
                WHERE id_clothes = %s AND deleted_at IS NOT NULL
            """
            result = ManageQuery._execute_query(query, id_clothes, fetch=True)
            return bool(result)
        except Error as e:
            logging.error(f"Error in is photo clothes deleted: {str(e)}")
            return False

    @staticmethod
    def exist_id_photo_user(id_photo):
        try:
            query = """
                    SELECT id_photo FROM photo_users
                    WHERE id_photo = %s AND deleted_at IS NULL
            """
            result = ManageQuery._execute_query(query, id_photo, fetch=True)
            if not result:
                result = None
            else:
                result = result[0][0]
            return result
        except Error as e:
            logging.error(f"Error exist id photo {str(e)}")

    @staticmethod
    def is_photo_clothes_unique(file_hash, data):
        """Проверяет, есть ли уже такое фото одежды у пользователя среди неудалённых"""
        try:
            query = """
                SELECT h.id_clothes FROM hash_photos_clothes AS h
                JOIN photo_clothes AS p
                ON h.id_clothes = p.id_clothes
                WHERE hash = %s AND p.id_user = %s AND p.id_category = %s
                AND p.id_subcategory = %s AND p.id_sub_subcategory = %s AND deleted_at IS NULL
                LIMIT 1
            """
            result = ManageQuery._execute_query(query, (
                file_hash, data["id_user"], data["id_category"], data["id_subcategory"], data["id_sub_subcategory"]),
                                                True)
            ret = True
            if result:
                ret = False
            return ret
        except Error as e:
            logging.error(f"Error in is_photo_clothes_unique {str(e)}")
            return None

    @staticmethod
    def is_photo_clothes_among_deleted(file_hash, id_user):
        """Проверяет, есть ли уже такое фото в гардеробе среди удалённых"""
        try:
            query = """
                SELECT h.id_photo FROM hash_photos_clothes AS h
                JOIN photo_clothes AS p
                ON h.id_clothes = p.id_clothes
                WHERE hash = %s AND p.id_user = %s AND deleted_at IS NOT NULL
                LIMIT 1
            """
            result = ManageQuery._execute_query(query, (file_hash, id_user), True)
            if not result:
                result = False
            else:
                result = result[0][0]
            return result
        except Error as e:
            logging.error(f"Error in is_photo_clothes_among_deleted {str(e)}")
            return None

    @staticmethod
    def is_photo_catalog_unique(file_hash, data):
        """Проверяет, есть ли уже такое фото одежды в каталоге среди неудалённых"""
        try:
            query = """
                SELECT h.id_clothes FROM hash_photos_catalog AS h
                JOIN photo_clothes AS p
                ON h.id_clothes = p.id_clothes
                WHERE hash = %s AND p.id_user = %s AND p.id_category = %s
                AND p.id_subcategory = %s AND p.id_sub_subcategory = %s AND deleted_at IS NULL
                LIMIT 1
            """
            result = ManageQuery._execute_query(query, (
                file_hash, data["id_user"], data["id_category"], data["id_subcategory"], data["id_sub_subcategory"]),
                                                True)
            ret = True
            if result:
                ret = False
            return ret
        except Error as e:
            logging.error(f"Error in is_photo_catalog_unique {str(e)}")
            return None

    @staticmethod
    def is_photo_catalog_among_deleted(file_hash, id_user):
        """Проверяет, есть ли уже такое фото в каталоге среди удалённых"""
        try:
            query = """
                SELECT h.id_photo FROM hash_photos_catalog AS h
                JOIN photo_clothes AS p
                ON h.id_clothes = p.id_clothes
                WHERE hash = %s AND p.id_user = %s AND deleted_at IS NOT NULL
                LIMIT 1
            """
            result = ManageQuery._execute_query(query, (file_hash, id_user), True)
            if not result:
                result = False
            else:
                result = result[0][0]
            return result
        except Error as e:
            logging.error(f"Error in is_photo_catalog_among_deleted {str(e)}")
            return None

    @staticmethod
    def is_photo_users_unique(file_hash, id_user):
        """Проверяет, есть ли уже такое фото у пользователя среди неудалённых"""
        try:
            query = """
                SELECT h.id_photo FROM hash_photos_users AS h
                JOIN photo_users AS p
                ON h.id_photo = p.id_photo
                WHERE hash = %s AND p.id_user = %s AND deleted_at IS NULL
                LIMIT 1
            """
            result = ManageQuery._execute_query(query, (file_hash, id_user), True)
            ret = True
            if result:
                ret = False
            return ret
        except Error as e:
            logging.error(f"Error in is_photo_users_unique {str(e)}")
            return None

    @staticmethod
    def is_photo_user_among_deleted(file_hash, id_user):
        """Проверяет, есть ли уже такое фото у пользователя среди удалённых"""
        try:
            query = """
                SELECT h.id_photo FROM hash_photos_users AS h
                JOIN photo_users AS p
                ON h.id_photo = p.id_photo
                WHERE hash = %s AND p.id_user = %s AND deleted_at IS NOT NULL
                LIMIT 1
            """
            result = ManageQuery._execute_query(query, (file_hash, id_user), True)
            if not result:
                result = False
            else:
                result = result[0][0]
            return result
        except Error as e:
            logging.error(f"Error in is_photo_user_among_deleted {str(e)}")
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
    def get_clothes_from_wardrobe_paginated(id_user, id_category, id_subcategory,
                                            id_sub_subcategory, limit=20,
                                            offset=0):  # Получает id_subcategory, id_category, id_sub_subcategory фото одежды по названию подкатегории
        try:
            query = """
                     SELECT id_clothes, photo_path FROM photo_clothes
                     WHERE id_user = %s AND id_category = %s AND id_subcategory = %s AND id_sub_subcategory = %s AND deleted_at IS NULL
                     LIMIT %s OFFSET %s
             """
            result = ManageQuery._execute_query(query, (
                id_user, id_category, id_subcategory, id_sub_subcategory, limit, offset), True)
            if not result:
                return None

            clothes_list = [{"id_clothes": row[0], "photo_path": row[1]} for row in result]
            return clothes_list
        except Error as e:
            logging.error(f"Error get_clothes_from_wardrobe_paginated {str(e)}")
            return None

    @staticmethod
    def get_clothes_from_catalog_paginated(id_category, id_subcategory, id_sub_subcategory, limit=20, offset=0):
        """
        Возвращает список одежды из каталога по указанной категории и подподкатегории.
        """
        try:
            query = """
                SELECT id_clothes, photo_path
                FROM photo_clothes
                WHERE id_category = %s AND id_subcategory = %s AND id_sub_subcategory = %s AND deleted_at IS NULL
                LIMIT %s OFFSET %s
            """
            result = ManageQuery._execute_query(query, (id_category, id_subcategory, id_sub_subcategory, limit, offset),
                                                fetch=True)
            if not result:
                result = None

            clothes = [{"id_clothes": row[0], "photo_path": row[1]} for row in result]
            return clothes
        except Error as e:
            logging.error(f"Error get_clothes_from_catalog_paginated {str(e)}")
            return None

    @staticmethod
    def count_clothes_in_wardrobe(id_user, id_category, id_subcategory, id_sub_subcategory):
        """
        Возвращает общее количество элементов одежды в гардеробе.
        """
        try:
            query = """
            SELECT COUNT(*) FROM photo_clothes
            WHERE id_user = %s AND id_category = %s AND id_subcategory = %s AND id_sub_subcategory = %s AND deleted_at IS NULL
            """
            result = ManageQuery._execute_query(query, (id_user, id_category, id_subcategory, id_sub_subcategory),
                                                fetch=True)
            if not result:
                result = None
            else:
                result = result[0][0]
            return result
        except Error as e:
            logging.error(f"Error count_clothes_in_wardrobe {str(e)}")
            return None

    @staticmethod
    def count_clothes_in_catalog(id_category, id_subcategory, id_sub_subcategory):
        """
        Возвращает общее количество элементов одежды в каталоге.
        """
        try:
            query = """
                 SELECT COUNT(*) FROM photo_clothes
                 WHERE id_category = %s AND id_subcategory = %s AND id_sub_subcategory = %s AND deleted_at IS NULL
             """
            result = ManageQuery._execute_query(query, (id_category, id_subcategory, id_sub_subcategory), fetch=True)
            if not result:
                result = None
            else:
                result = result[0][0]
            return result
        except Error as e:
            logging.error(f"Error count_clothes_in_catalog {str(e)}")
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
    def add_hash_photos_clothes_catalog(id_clothes, hash):
        ret = False

        try:
            query = """
                    INSERT INTO hash_photos_catalog(id_clothes, hash)
                    VALUES (%s, %s)
            """
            ManageQuery._execute_query(query, (id_clothes, hash))
            ret = True
        except Error as e:
            logging.error(f"Error add_hash_photos_catalog {str(e)}")
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
    def add_photo_clothes(photo_path, id_category, id_subcategory, id_sub_subcategory, id_user,
                          is_cut=True):  # Добавляет фото одежды в базу данных
        ret = False

        try:
            query = """
                    INSERT INTO photo_clothes (id_user, photo_path, id_category, id_subcategory, id_sub_subcategory, is_cut)
                    VALUES (%s, %s, %s, %s, %s, %s) returning id_clothes
            """
            id_clothes = ManageQuery._execute_query(query, (
                id_user, photo_path, id_category, id_subcategory, id_sub_subcategory, is_cut), fetch_insert=True)
            logging.info(f"Photo clothes added successfully")
            ret = id_clothes
        except Error as e:
            logging.error(f"Error add photo clothes {str(e)}")
        return ret

    @staticmethod
    def delete_hash_photos_clothes(id_clothes):
        try:
            query = """
                    DELETE FROM hash_photos_clothes
                    WHERE id_clothes = %s RETURNING id_clothes
            """
            result = ManageQuery._execute_query(query, id_clothes, fetch_insert=True)

            if not result:
                result = None
            return result
        except Error as e:
            logging.error(f"Error delete hash photos clothes {str(e)}")
            return False

    @staticmethod
    def delete_hash_photos_catalog(id_clothes):
        try:
            query = """
                    DELETE FROM hash_photos_catalog
                    WHERE id_clothes = %s RETURNING id_clothes
            """
            result = ManageQuery._execute_query(query, id_clothes, fetch_insert=True)

            if not result:
                result = None
            return result
        except Error as e:
            logging.error(f"Error delete hash photos catalog {str(e)}")
            return False

    @staticmethod
    def delete_photo_clothes(id_clothes, id_user):  # Мягкое удаление фото одежды из базы данных
        if not id_clothes:
            logging.error("id clothes is empty")
            return {'status': 'error', 'message': 'Clothing ID not specified'}

        try:
            # Проверяем существование записи
            if not ManageQuery.exist_id_clothes(id_clothes, id_user):
                return {'status': 'error', 'message': f'Clothes with ID {id_clothes} not found'}

            # Проверяем, не удалена ли уже запись
            if ManageQuery.is_clothes_deleted(id_clothes, id_user):
                return {'status': 'error', 'message': f'Clothes with ID {id_clothes} have already been removed'}

            if not ManageQuery.get_id_user_by_id(id_user):
                return {'status': 'error', 'message': f'User with ID {id_user} not found'}

            # Выполняем мягкое удаление
            query = """
                UPDATE photo_clothes
                SET deleted_at = CURRENT_TIMESTAMP
                WHERE id_clothes = %s AND id_user = %s
                RETURNING id_clothes
            """
            result = ManageQuery._execute_query(query, (id_clothes, id_user), fetch_insert=True)

            # if result and ManageQuery.delete_hash_photos_clothes(id_clothes):
            if result:
                return {'status': 'success', 'id': result[0]}
            return {'status': 'error', 'message': 'Unable to perform deletion'}

        except Error as e:
            logging.error(f"Error delete photo clothes: {str(e)}")
            return {'status': 'error', 'message': f'Database error: {str(e)}'}

    @staticmethod
    def delete_photo_clothes_catalog(id_clothes):  # Мягкое удаление фото одежды из каталога
        if not id_clothes:
            logging.error("id clothes is empty")
            return {'status': 'error', 'message': 'ID одежды не указан'}

        try:
            # Проверяем существование записи
            if not ManageQuery.exist_id_clothes_catalog(id_clothes):
                return {'status': 'error', 'message': f'Clothes with id {id_clothes} not found'}

            # Проверяем, не удалена ли уже запись
            if ManageQuery.is_clothes_deleted_catalog(id_clothes):
                return {'status': 'error', 'message': f'Clothes with ID {id_clothes} have already been removed'}

            # Выполняем мягкое удаление
            query = """
                UPDATE photo_clothes
                SET deleted_at = CURRENT_TIMESTAMP
                WHERE id_clothes = %s
                RETURNING id_clothes
            """
            result = ManageQuery._execute_query(query, id_clothes, fetch_insert=True)

            # if result and ManageQuery.delete_hash_photos_catalog(id_clothes):
            if result:
                return {'status': 'success', 'id': result[0]}
            return {'status': 'error', 'message': 'Unable to perform deletion'}

        except Error as e:
            logging.error(f"Error delete photo clothes: {str(e)}")
            return {'status': 'error', 'message': f'Database error: {str(e)}'}

    @staticmethod
    def is_clothes_deleted(id_clothes, id_user) -> bool:
        """Проверяет, удалена ли уже запись"""
        try:
            query = """
                SELECT id_clothes FROM photo_clothes
                WHERE id_clothes = %s AND id_user = %s AND deleted_at IS NOT NULL
            """
            result = ManageQuery._execute_query(query, (id_clothes, id_user), fetch=True)
            return bool(result)
        except Error as e:
            logging.error(f"Error in is_clothes_deleted: {str(e)}")
            return False

    @staticmethod
    def is_clothes_deleted_catalog(id_clothes):
        try:
            query = """
                SELECT id_clothes FROM photo_clothes
                WHERE id_clothes = %s 
                AND deleted_at IS NOT NULL
                AND id_user IN (SELECT id_user FROM users WHERE is_admin = true)
            """
            result = ManageQuery._execute_query(query, id_clothes, fetch=True)
            return bool(result)
        except Error as e:
            logging.error(f"Error in is_clothes_deleted_catalog: {str(e)}")
            return False

    @staticmethod
    def get_user_photos_paginated(id_user, limit=20, offset=0):
        try:
            query = """
                    SELECT id_photo, photo_path
                    FROM photo_users
                    WHERE id_user = %s AND deleted_at IS NULL
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
            query = """
                    SELECT COUNT(*) FROM photo_users
                    WHERE id_user = %s AND deleted_at IS NULL
            """
            result = ManageQuery._execute_query(query, id_user, True)
            if not result:
                result = None
            return result[0][0]
        except Error as e:
            logging.error(f"Error count user photos {str(e)}")

    @staticmethod
    def exist_id_clothes(id_clothes, id_user):
        """
        Проверяет существование одежды по ID
        """
        try:
            query = """
                    SELECT id_clothes FROM photo_clothes
                    WHERE id_clothes = %s AND id_user = %s AND deleted_at IS NULL
            """
            result = ManageQuery._execute_query(query, (id_clothes, id_user), fetch=True)
            if result:
                return {
                    'status': 'success',
                    'id': result[0][0]
                }
            return {'status': 'error', 'message': f'Clothes with ID {id_clothes} not found for user {id_user}'}
        except Error as e:
            logging.error(f"Error recovery_photos_wardrobe_db {str(e)}")

    @staticmethod
    def exist_id_clothes_catalog(id_clothes):
        """
        Проверяет только существование одежды в каталоге
        """
        try:
            query = """
                SELECT id_clothes FROM photo_clothes
                WHERE id_clothes = %s 
                AND deleted_at IS NULL
                AND id_user IN (SELECT id_user FROM users WHERE is_admin = true)
            """
            result = ManageQuery._execute_query(query, id_clothes, fetch=True)
            if result:
                return {
                    'status': 'success',
                    'id': result[0][0]
                }
            return {'status': 'error', 'message': f'Clothes with ID {id_clothes} not found in catalog'}
        except Error as e:
            logging.error(f"Error exist_id_clothes_catalog: {str(e)}")

    @staticmethod
    def get_path_clothes(id_clothes):
        try:
            query = """
                SELECT photo_path FROM photo_clothes
                WHERE id_clothes = %s AND deleted_at IS NULL
            """
            result = ManageQuery._execute_query(query, id_clothes, fetch=True)
            if not result:
                result = None
            else:
                result = result[0][0]
            return result
        except Error as e:
            logging.error(f"Error get path clothes {str(e)}")

    @staticmethod
    def get_admin_clothes(limit=20, offset=0):
        """
        Возвращает список одежды, добавленной администратором.
        """
        try:
            # Получаем список ID админов из .env
            admin_list = tuple(map(int, os.getenv("ADMIN_LIST", "").split(",")))
            if not admin_list:
                return None

            # Формируем placeholders для IN (%s, %s, ...)
            placeholders = ', '.join(['%s'] * len(admin_list))

            query = f"""
                SELECT id_clothes, photo_path, id_category, id_subcategory, id_sub_subcategory
                FROM photo_clothes
                WHERE id_user IN ({placeholders})
                LIMIT %s OFFSET %s
            """

            # Объединяем параметры: сначала ID админов, потом limit и offset
            params = admin_list + (limit, offset)

            result = ManageQuery._execute_query(query, params, fetch=True)
            return result if result else None

        except Error as e:
            logging.error(f"Error get_admin_clothes {str(e)}")
            return None

    @staticmethod
    def count_admin_clothes():
        """
        Подсчитывает количество элементов одежды, добавленных администраторами (по id_user).
        """
        try:
            admin_list = tuple(map(int, os.getenv("ADMIN_LIST", "").split(",")))
            if not admin_list:
                return 0  # если переменная пустая, возвращаем 0

            placeholders = ', '.join(['%s'] * len(admin_list))
            query = f"""
                SELECT COUNT(*) FROM photo_clothes
                WHERE id_user IN ({placeholders})
            """
            result = ManageQuery._execute_query(query, admin_list, fetch=True)
            if not result:
                result = None
            return result[0][0]
        except Error as e:
            logging.error(f"Error count user photos {str(e)}")

    @staticmethod
    def get_name_category(id_category):
        """
        Возвращает название категории по её id.
        """
        try:
            query = """
                SELECT category FROM category_clothes 
                WHERE id_category = %s
            """
            result = ManageQuery._execute_query(query, (id_category,), fetch=True)
            if not result:
                result = None
            else:
                result = result[0][0]
            return result
        except Error as e:
            logging.error(f"Error get id category_photos {str(e)}")
            return None

    @staticmethod
    def get_name_subcategory(id_subcategory):
        """
        Возвращает название подкатегории по её id.
        """
        try:
            query = """
                SELECT subcategory FROM subcategory_clothes 
                WHERE id_subcategory = %s
            """
            result = ManageQuery._execute_query(query, (id_subcategory,), fetch=True)
            if not result:
                result = None
            else:
                result = result[0][0]
            return result
        except Error as e:
            logging.error(f"Error get id subcategory_photos {str(e)}")
            return None

    @staticmethod
    def get_name_sub_subcategory(id_sub_subcategory):
        """
        Возвращает название под-подкатегории по её id.
        """
        try:
            query = """
                SELECT sub_subcategory FROM sub_subcategory_clothes 
                WHERE id_sub_subcategory = %s
            """
            result = ManageQuery._execute_query(query, (id_sub_subcategory,), fetch=True)
            if not result:
                result = None
            else:
                result = result[0][0]
            return result
        except Error as e:
            logging.error(f"Error get id sub_subcategory_photos {str(e)}")
            return None

    @staticmethod
    def recovery_photos_wardrobe_db(id_clothes, id_user):
        """
        Восстанавливает удалённое фото одежды из гардероба
        :param id_clothes:
        :param id_user:
        :return:
        """
        try:
            query = """
                    UPDATE photo_clothes
                    SET deleted_at = NULL
                    WHERE id_clothes = %s AND id_user = %s
                    RETURNING id_clothes
            """
            result = ManageQuery._execute_query(query, (id_clothes, id_user), fetch_insert=True)
            if result:
                return {
                    'status': 'success',
                    'id': result[0]
                }
            return {'status': 'error', 'message': 'Не удалось выполнить восстановление фото одежды из гардероба'}
        except Error as e:
            logging.error(f"Error recovery_photos_wardrobe_db {str(e)}")

    @staticmethod
    def recovery_photos_human_db(id_photo, id_user):
        """
        Восстанавливает удалённое фото человека
        :param id_photo:
        :param id_user:
        :return:
        """
        try:
            query = """
                    UPDATE photo_users
                    SET deleted_at = NULL
                    WHERE id_photo = %s AND id_user = %s
                    RETURNING id_photo
            """
            result = ManageQuery._execute_query(query, (id_photo, id_user), fetch_insert=True)
            if result:
                return {
                    'status': 'success',
                    'id': result[0]
                }
            return {'status': 'error', 'message': 'Не удалось выполнить восстановление фото человека'}
        except Error as e:
            logging.error(f"Error recovery_photos_human_db {str(e)}")

    @staticmethod
    def get_deleted_photos_by_type(id_user, photo_type, limit=20, offset=0):
        """
        Возвращает список удаленных фотографий по типу: «пользователи» или «одежда»
        """
        try:
            if photo_type == "users":
                table_name = "photo_users"
                id_column = "id_photo"
            elif photo_type == "clothes":
                table_name = "photo_clothes"
                id_column = "id_clothes"
            else:
                raise ValueError("Unsupported photo type")

            query = f"""
                SELECT {id_column}, photo_path
                FROM {table_name}
                WHERE id_user = %s AND deleted_at IS NOT NULL   
                LIMIT %s OFFSET %s
            """
            result = ManageQuery._execute_query(query, (id_user, limit, offset), fetch=True)
            if not result:
                result = None
            else:
                result = [{"id_photo": row[0], "photo_path": row[1]} for row in result]
            return result
        except Error as e:
            logging.error(f"Error getting deleted photos: {str(e)}")
            return None

    @staticmethod
    def exist_id_user(id_user):
        """
        Проверяет существование пользователя по его id в бд
        :param id_user:
        :return:
        """
        try:
            query = """
                    SELECT id_user FROM users
                    WHERE id_user = %s
            """
            result = ManageQuery._execute_query(query, id_user, fetch=True)
            if not result:
                result = None
            else:
                result = [0][0]

        except Error as e:
            raise
        return None

    @staticmethod
    def is_photo_belongs_to_user(id_photo, id_user):
        """
        Проверяет, принадлежит ли фото пользователю
        """
        try:
            query = """
                SELECT id_photo FROM photo_users
                WHERE id_photo = %s AND id_user = %s AND deleted_at IS NULL
            """
            result = ManageQuery._execute_query(query, (id_photo, id_user), fetch=True)
            return bool(result)
        except Exception as e:
            logging.error(f"Error checking photo ownership: {str(e)}")
            return False

