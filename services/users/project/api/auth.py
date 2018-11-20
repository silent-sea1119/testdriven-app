from flask import Blueprint, jsonify, request
from sqlalchemy import exc, or_

from project.api.models import User
from project import db, bcrypt

auth_blueprint = Blueprint("auth", __name__)


@auth_blueprint.route("/auth/register", methods=["POST"])
def register_user():
    post_data = request.get_json()
    response_object = {"status": "fail", "message": "Invalid payload."}

    if not post_data:
        return jsonify(response_object), 400

    username = post_data.get("username")
    email = post_data.get("email")
    password = post_data.get("password")

    try:
        user = User.query.filter(or_(User.username == username, User.email == email)).first()
        if not user:
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()

            auth_token = new_user.encode_auth_token(new_user.id)
            response_object["status"] = "success"
            response_object["message"] = "Successfully registered."
            response_object["auth_token"] = auth_token.decode()
            return jsonify(response_object), 201
        else:
            response_object["message"] = "Sorry. That user already exists."
            return jsonify(response_object), 400
    except (exc.IntegrityError, ValueError):
        db.session.rollback()
        return jsonify(response_object), 400


@auth_blueprint.route("/auth/login", methods=["POST"])
def login_user():
    post_data = request.get_json()
    response_object = {"status": "fail", "message": "Invalid payload."}

    if not post_data:
        return jsonify(response_object), 400

    email = post_data.get("email")
    password = post_data.get("password")

    try:
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            auth_token = user.encode_auth_token(user.id)
            if auth_token:
                response_object["status"] = "success"
                response_object["message"] = "Successfully logged in."
                response_object["auth_token"] = auth_token.decode()
                return jsonify(response_object), 200
        else:
            response_object["message"] = "User does not exist."
            return jsonify(response_object), 404
    except Exception:
        response_object["message"] = "Try again."
        return jsonify(response_object), 500


@auth_blueprint.route("/auth/logout", methods=["GET"])
def logout_user():
    auth_header = request.headers.get("Authorization")
    response_object = {"status": "fail", "message": "Provide a valid auth token."}

    if auth_header:
        auth_token = auth_header.split(" ")[1]
        resp = User.decode_auth_token(auth_token)
        if not isinstance(resp, str):
            response_object["status"] = "success"
            response_object["message"] = "Successfully logged out."
            return jsonify(response_object), 200
        else:
            response_object["message"] = resp
            return jsonify(response_object), 401
    else:
        return jsonify(response_object), 403


@auth_blueprint.route("/auth/status", methods=["GET"])
def get_user_status():
    auth_header = request.headers.get("Authorization")
    response_object = {"status": "fail", "message": "Provide a valid auth token."}

    if auth_header:
        auth_token = auth_header.split(" ")[1]
        resp = User.decode_auth_token(auth_token)
        if not isinstance(resp, str):
            user = User.query.filter_by(id=resp).first()
            response_object["status"] = "success"
            response_object["message"] = "Success."
            response_object["data"] = user.to_json()
            return jsonify(response_object), 200
        response_object["message"] = resp
        return jsonify(response_object), 401
    else:
        return jsonify(response_object), 401
