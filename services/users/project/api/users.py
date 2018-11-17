from flask import Blueprint, jsonify, request, render_template
from sqlalchemy import exc

from project.api.models import User
from project import db

users_blueprint = Blueprint("users", __name__, template_folder="./templates")


@users_blueprint.route("/users/ping", methods=["GET"])
def ping_pong():
    return jsonify({"status": "success", "message": "pong!"})


@users_blueprint.route("/users", methods=["POST"])
def add_user():
    post_data = request.get_json()
    response_object = {"status": "fail", "message": "Invalid payload."}
    if not post_data:
        return jsonify(response_object), 400

    username = post_data.get("username")
    email = post_data.get("email")

    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            db.session.add(User(username=username, email=email))
            db.session.commit()
            response_object = {"status": "success", "message": f"{email} was added!"}
            return jsonify(response_object), 201
        else:
            response_object["message"] = "Sorry. That email already exists."
            return jsonify(response_object), 400
    except exc.IntegrityError:
        db.session.rollback()
        return jsonify(response_object), 400


@users_blueprint.route("/users/<user_id>", methods=["GET"])
def get_single_user(user_id):
    response_object = {"status": "fail", "message": "User does not exist"}
    try:
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify(response_object), 404
        response_object = {
            "status": "success",
            "data": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "active": user.active,
            },
        }
        return jsonify(response_object), 200
    except (ValueError, exc.DataError):
        return jsonify(response_object), 404


@users_blueprint.route("/users", methods=["GET"])
def get_all_users():
    response_object = {
        "status": "success",
        "data": {"users": [user.to_json() for user in User.query.all()]},
    }
    return jsonify(response_object), 200


@users_blueprint.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        db.session.add(User(username=username, email=email))
        db.session.commit()
    users = User.query.all()
    return render_template("index.html", users=users)
