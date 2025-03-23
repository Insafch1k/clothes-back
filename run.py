from flask import Flask
from flask_cors import CORS
from __init__ import all_blueprints

app = Flask(__name__)

app.register_blueprint(all_blueprints)

CORS(app)

if __name__ == "__main__":
     app.run(debug=True)
