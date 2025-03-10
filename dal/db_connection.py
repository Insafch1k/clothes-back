import os

import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv, find_dotenv
import logging

load_dotenv(find_dotenv())


class DBConnection:
    @staticmethod
    def get_con():
        try:
            # Подключение к базе данных
            connection = psycopg2.connect(
                dbname=os.getenv('DBNAME'),
                user=os.getenv('USER'),
                password=os.getenv('PASSWORD'),
                host=os.getenv('HOST'),
                port=os.getenv('PORT')
            )
            # logging.info("Database connection established successfully")
            return connection
        except Error as e:
            logging.error(f"Error connecting to the database: {str(e)}")
            return None
