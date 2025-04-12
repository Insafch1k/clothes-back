from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from dal.auth_dal import Authenticate

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/login', methods=['POST'])
def standard_login():
    """Аутентификация по логину и паролю"""
    data = request.get_json()
    username = data.get('name')  # Используем 'name' вместо 'username' согласно вашей БД
    password = data.get('password')

    if not username or not password:
        return jsonify({'status': 'error', 'message': 'Name and password required'}), 400

    result = Authenticate.authenticate_user_by_name_password(username, password)
    if result is None or result["status"] == "error":
        return jsonify(result), 401

    # Создаём токены
    access_token = create_access_token(identity=result["id_user"])
    refresh_token = create_refresh_token(identity=result["id_user"])

    return jsonify({
        'status': 'success',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'id_user': result["id_user"]
    })


@auth_blueprint.route('/login/telegram', methods=['POST'])
def telegram_login():
    """Аутентификация через Telegram"""
    data = request.get_json()
    tg_id = data.get('tg_id')

    if not tg_id:
        return jsonify({
            'status': 'error',
            'message': 'Telegram ID required'
        }), 400

    # Находим или создаём пользователя
    result = Authenticate.authenticate_user_by_tg_id(tg_id)
    if result["status"] == "error":
        return jsonify(result), 500

    # Создаём токены
    access_token = create_access_token(identity=result["id_user"])
    refresh_token = create_refresh_token(identity=result["id_user"])

    return jsonify({
        'status': 'success',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'id_user': result["id_user"]
    })


@auth_blueprint.route('/link-account', methods=['POST'])
@jwt_required()
def link_telegram_account():
    """Привязка Telegram ID к существующему аккаунту"""
    id_user = get_jwt_identity()
    tg_id = request.json.get('tg_id')

    if not tg_id:
        return jsonify({'status': 'error', 'message': 'Telegram ID required'}), 400

    # Проверяем, не привязан ли уже этот tg_id к другому аккаунту
    if Authenticate.check_tg_id_exists(tg_id):
        return jsonify({'status': 'error', 'message': 'Telegram ID already linked'}), 400

    result = Authenticate.link_telegram_account_db(tg_id, id_user)
    if result["status"] == "error":
        return jsonify(result), 500

    return jsonify(result)


@auth_blueprint.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Обновление access token"""
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user)
    return jsonify({'access_token': new_token})
