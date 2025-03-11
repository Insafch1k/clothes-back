import psycopg2
from .db_connection import DBConnection
from psycopg2 import Error
import logging


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
                        if result and len(result) == 1 and len(result[0]) == 1:  # Если результат содержит одно значение
                            result = result[0][0]  # Вернуть это значение
                        return result  # Иначе вернуть весь результат

                    con.commit()
                except Error as e:
                    logging.error(f"Error executing query: {str(e)}")
                    con.rollback()
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
            return result
        except Error as e:
            logging.error(f"Error get id category_photos {str(e)}")
            return None

    @staticmethod
    def photo_in_binary(photo):  # Переводит фото в бинарный вид
        try:
            binary_photo = psycopg2.Binary(photo)
            return binary_photo
        except Error as e:
            logging.error(f"Error photo in binary {str(e)}")
            return None

    # @staticmethod # Не используется
    # def category_photos_not_exists(category):  # Проверяет, существует ли данная категория фото в базе данных
    #     try:
    #         query = """
    #                 SELECT EXISTS (
    #                     SELECT id_category FROM category_photos
    #                     WHERE category = %s
    #                 )
    #         """
    #         result = ManageQuery._execute_query(query, category, True)
    #         ret = True
    #         if result:
    #             ret = False
    #         return ret
    #     except Error as e:
    #         logging.error(f"Error checking category photo existence: {str(e)}")
    #         return False

    @staticmethod
    def photo_users_not_exist(photo, user_name):  # Проверяет, существует ли фото в базе данных у этого человека
        try:
            binary_photo = ManageQuery.photo_in_binary(photo)
            id_user = ManageQuery.get_id_user(user_name)
            query = """
                    SELECT id_photo FROM photo_users
                    WHERE photo = %s AND id_user = %s
            """
            result = ManageQuery._execute_query(query, (binary_photo, id_user), True)
            ret = True
            if result:
                ret = False
            return ret
        except Error as e:
            logging.error(f"Error photo not exist {str(e)}")
            return None

    @staticmethod
    def check_args_add_photo(id_user, id_category, binary_photo, user_name, category):
        ret = True
        if id_user is None:
            logging.error(f"User '{user_name}' not found")
            ret = False
        if id_category is None:
            logging.error(f"Category '{category}' not found")
            ret = False
        if binary_photo is None:
            logging.error("Failed to convert photo to binary")
            ret = False
        return ret

    @staticmethod
    def add_photo_user(user_name, photo, category, is_cut=True):  # Добавляет фото человека в базу данных
        ret = False
        # if ManageQuery.category_photos_not_exists(category):  # Проверка существования категории
        #     logging.error(f"Category '{category}' does not exist in category_photos")
        #     return ret

        if ManageQuery.photo_users_not_exist(photo,
                                             user_name):  # Проверяет, существует ли фото человека в базе данных у этого человека
            try:
                id_user = ManageQuery.get_id_user(user_name)
                id_category = ManageQuery.get_id_category_photos(category)
                binary_photo = ManageQuery.photo_in_binary(photo)
                if ManageQuery.check_args_add_photo(id_user, id_category, binary_photo, user_name, category):
                    query = """
                            INSERT INTO photo_users (id_user, photo, id_category, is_cut)
                            VALUES (%s, %s, %s, %s)
                    """
                    ManageQuery._execute_query(query, (id_user, binary_photo, id_category, is_cut))
                    logging.info(f"Photo added successfully for user {user_name}")
                    ret = True
                else:
                    logging.error("Invalid user id, category id, or photo binary")
            except Error as e:
                logging.error(f"Error add photo user {str(e)}")
        else:
            logging.warning("Это фото уже есть в базе данных у этого человека")
        return ret

    @staticmethod
    def delete_photo_user(photo):  # Удаляет фото человека из базы данных
        ret = False
        try:
            binary_photo = ManageQuery.photo_in_binary(photo)
            if binary_photo is None:
                logging.error("Delete photo user: failed to convert photo to binary")
                return ret

            if binary_photo:
                query = """
                        DELETE FROM photo_users
                        WHERE photo = %s
                """
                ManageQuery._execute_query(query, binary_photo)
                ret = True
            else:
                logging.error("Invalid photo binary")
        except Error as e:
            logging.error(f"Error delete photo user: {str(e)}")
        return ret

    @staticmethod
    def photo_clothes_not_exist(photo, user_name):  # Проверяет, существует ли фото в базе данных у этого человека
        try:
            binary_photo = ManageQuery.photo_in_binary(photo)
            id_user = ManageQuery.get_id_user(user_name)
            query = """
                    SELECT id_clothes FROM photo_clothes
                    WHERE photo = %s AND id_user = %s
            """
            result = ManageQuery._execute_query(query, (binary_photo, id_user), True)
            ret = True
            if result:
                ret = False
            return ret
        except Error as e:
            logging.error(f"Error photo not exist {str(e)}")
            return None

    # @staticmethod  # Не используется
    # def category_clothes_not_exists(category):  # Проверяет, существует ли данная категория одежды в базе данных
    #     try:
    #         query = """
    #                 SELECT EXISTS (
    #                     SELECT id_category FROM category_clothes
    #                     WHERE category = %s
    #                 )
    #         """
    #         result = ManageQuery._execute_query(query, category, True)
    #         ret = True
    #         if result:
    #             ret = False
    #         return ret
    #     except Error as e:
    #         logging.error(f"Error checking category clothes existence: {str(e)}")
    #         return False

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
            return result
        except Error as e:
            logging.error(f"Error get id category_photos {str(e)}")
            return None

    @staticmethod
    def add_photo_clothes(user_name, photo, category, is_cut=True):  # Добавляет фото одежды в базу данных
        ret = False
        # if ManageQuery.category_clothes_not_exists(category):  # Проверка существования категории
        #     logging.error(f"Category '{category}' does not exist in category_clothes")
        #     return ret

        if ManageQuery.photo_clothes_not_exist(photo,
                                               user_name):  # Проверяет, существует ли фото одежды в базе данных у этого человека
            try:
                id_user = ManageQuery.get_id_user(user_name)
                id_category = ManageQuery.get_id_category_clothes(category)
                binary_photo = ManageQuery.photo_in_binary(photo)
                if ManageQuery.check_args_add_photo(id_user, id_category, binary_photo, user_name, category):
                    query = """
                            INSERT INTO photo_clothes (id_user, photo, id_category, is_cut)
                            VALUES (%s, %s, %s, %s)
                    """
                    ManageQuery._execute_query(query, (id_user, binary_photo, id_category, is_cut))
                    logging.info(f"Photo clothes added successfully for user {user_name}")
                    ret = True
                else:
                    logging.error("Invalid user id, category id, or photo binary")
            except Error as e:
                logging.error(f"Error add photo user {str(e)}")
        else:
            logging.warning("Это фото одежды уже есть в базе данных у этого человека")
        return ret

    @staticmethod
    def delete_photo_clothes(photo):  # Удаляет фото одежды из базы данных
        ret = False
        try:
            binary_photo = ManageQuery.photo_in_binary(photo)
            if binary_photo is None:
                logging.error("Delete photo clothes: failed to convert photo to binary")
                return ret

            if binary_photo:
                query = """
                        DELETE FROM photo_clothes
                        WHERE photo = %s
                """
                ManageQuery._execute_query(query, binary_photo)
                ret = True
            else:
                logging.error("Invalid photo binary")
        except Error as e:
            logging.error(f"Error delete photo clothes: {str(e)}")
        return ret
