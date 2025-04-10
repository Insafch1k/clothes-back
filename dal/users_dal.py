from dal.db_connection import DBConnection
import logging
from dal.db_query import ManageQuery


class UsersDAL:
    @staticmethod
    def auto_register_user_if_not_exists(id_user):
        try:
            query = """
                    SELECT id_user FROM users
                    WHERE id_user = %s
            """
            result = ManageQuery._execute_query(query, (id_user,), fetch=True)
            if result:
                return {"error": "User already exists!"}, 400

            insert_query = """
                        INSERT INTO users (id_user, name)
                        VALUES (%s, %s)
                       """
            default_name = f"user_{id_user}"
            ManageQuery._execute_query(insert_query, (id_user, default_name))

            return {"message": "User successfully registered"}, 201

        except Exception as e:
            logging.error(f"Error while registering user: {str(e)}")
            return {"error": f"Server error: {str(e)}"}, 500
