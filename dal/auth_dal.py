from psycopg2 import Error
import logging

from dal.db_connection import DBConnection


class Authenticate:
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
                except Error:
                    # logging.error(f"Error executing query: {str(e)}")
                    con.rollback()
                    raise

    @staticmethod
    def authenticate_user_by_name_password(username, password):
        """
        Проверяет учетные данные пользователя по name и password и возвращает id_user если успешно
        """
        try:
            query = """
                SELECT id_user FROM users 
                WHERE name = %s AND password = crypt(%s, password)
            """
            result = Authenticate._execute_query(query, (username, password), fetch=True)
            if not result:
                result = {
                    "status": "error",
                    "message": f"Пользователь username {username} не найден"
                }
            else:
                result = {
                    "status": "success",
                    "id_user": result[0][0]
                }
            return result
        except Error as e:
            logging.error(f"Error authenticating user: {str(e)}")
            return None

    @staticmethod
    def register_user_by_tg_id_if_not_exists(tg_id):
        """
        Создаёт нового пользователя по tg_id
        :return:
        """
        try:
            result = None
            query = """
                    INSERT INTO users(tg_id)
                    VALUES (%s) RETURNING id_user
            """
            id_user = Authenticate._execute_query(query, tg_id, fetch_insert=True)
            if not id_user:
                result = {
                    "status": "error",
                    "message": f"Не удалось добавить пользователя с tg_id {tg_id}"
                }
            else:
                result = {
                    "status": "success",
                    "id_user": id_user
                }
            return result
        except Error:
            raise

    @staticmethod
    def authenticate_user_by_tg_id(tg_id):
        """
        Проверяет учетные данные пользователя по tg_id, добавляет пользователя,
        если он не зарегистрирован и возвращает id_user если успешно
        """
        try:
            query = """
                SELECT id_user FROM users 
                WHERE tg_id = %s
            """
            result = Authenticate._execute_query(query, tg_id, fetch=True)
            if not result:
                result = Authenticate.register_user_by_tg_id_if_not_exists(tg_id)
            else:
                result = {
                    "status": "success",
                    "id_user": result[0][0]
                }
            return result
        except Error as e:
            logging.error(f"Error authenticating user: {str(e)}")
            return None

    @staticmethod
    def check_tg_id_exists(tg_id):
        """Проверяет существование пользователя с таким Telegram ID"""
        query = """
                SELECT id_user FROM users
                WHERE tg_id = %s
        """
        result = Authenticate._execute_query(query, (tg_id,), fetch=True)
        return bool(result)

    @staticmethod
    def link_telegram_account_db(tg_id, id_user):
        # Обновляем запись пользователя
        query = """
                UPDATE Users SET tg_id = %s
                WHERE id_user = %s RETURNING id_user
        """
        id_user = Authenticate._execute_query(query, (tg_id, id_user), fetch_insert=True)
        result = None
        if not id_user:
            result = {
                "status": "error",
                "message": "Не удалось добавить tg id к существующему аккаунту"
            }
        else:
            result = {
                'status': 'success',
                'message': 'Telegram account linked successfully',
                "id_user": id_user
            }
        return result
