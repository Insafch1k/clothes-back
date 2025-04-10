from flask import Blueprint, request, jsonify
from bl.users_bl import UsersBL
import logging

routes_for_users = Blueprint("routes_for_users", __name__)


@routes_for_users.route("/register", methods=["POST"])
def register_user():
    try:
        data = request.get_json()
        id_user = data.get("id_user")

        if not id_user:
            return ({"error": "id_user is required"}), 400

        response, status_code = UsersBL.register_user(id_user)
        return response, status_code

    except Exception as e:
        logging.exception("Error processing registration request")
        return jsonify({"error": f"Server error: {str(e)}"}), 500
