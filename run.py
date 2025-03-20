#from db_query import ManageQuery
from flask import Flask
import logging
from routes.background_routes import background_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# app.config.from_object(__name__)
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
#
# app.config.update(dict(DATABASE=os.path.join(app.root_path, os.getenv("DBNAME"))))

#logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

app.register_blueprint(background_bp, url_prefix="/background")

# def test_add_photo_user():
#     with open("1.jpg", "rb") as file:
#         img = file.read()
#         m = ManageQuery()
#         if m.add_photo_user('Dod', img, "Full"):
#             logging.info("Test passed: Photo added successfully")
#         else:
#             logging.error("Test failed: Photo not added")
        # m.delete_photo_user(img)


#test_add_photo_user()
if __name__ == "__main__":
     app.run(debug=True)
