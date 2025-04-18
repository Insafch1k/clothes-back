from flask import Flask
from flask_cors import CORS
from __init__ import main_blueprint  # Измененный импорт
from flask_jwt_extended import JWTManager

from bl.auth.jwt_manager import setup_jwt

app = Flask(__name__)
CORS(app)

# Настройка JWT
setup_jwt(app)

# Регистрация основного Blueprint
app.register_blueprint(main_blueprint)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
