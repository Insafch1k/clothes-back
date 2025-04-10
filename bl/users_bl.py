from dal.users_dal import UsersDAL
from flask import jsonify
import logging


class UsersBL:
    @staticmethod
    def register_user(id_user):
        return UsersDAL.auto_register_user_if_not_exists(id_user)
