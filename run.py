from flask import Flask
from flask_cors import CORS
from __init__ import main_blueprint  # Измененный импорт

app = Flask(__name__)
CORS(app)

# Регистрация основного Blueprint
app.register_blueprint(main_blueprint)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)