import psycopg2
from db_query import ManageQuery
from db_connection import DBConnection
from flask import Flask
import os
import logging

# app = Flask(__name__)
# app.config.from_object(__name__)
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
#
# app.config.update(dict(DATABASE=os.path.join(app.root_path, os.getenv("DBNAME"))))

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')


def test_add_photo_user():
    with open("1.jpg", "rb") as file:
        img = file.read()
        m = ManageQuery()
        if m.add_photo_user('Dod', img, "Full"):
            logging.info("Test passed: Photo added successfully")
        else:
            logging.error("Test failed: Photo not added")
        # m.delete_photo_user(img)


test_add_photo_user()
# if __name__ == "__main__":
#     app.run(debug=True)
