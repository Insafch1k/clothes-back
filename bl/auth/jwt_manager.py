from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token
from flask import jsonify
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

jwt = JWTManager()


def setup_jwt(app):
    app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')  # Измените в production
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

    jwt.init_app(app)

    # Callbacks для кастомизации ответов
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'status': 'error',
            'message': 'Token has expired'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'status': 'error',
            'message': 'Invalid token'
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'status': 'error',
            'message': 'Authorization required'
        }), 401


def create_tokens(identity, additional_claims=None):
    access_token = create_access_token(
        identity=identity,
        additional_claims=additional_claims
    )
    refresh_token = create_refresh_token(identity=identity)
    return access_token, refresh_token
