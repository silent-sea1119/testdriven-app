import datetime as dt

import jwt
from flask import current_app
from sqlalchemy.sql import func

from project import db, bcrypt


class User(db.Model):  # type: ignore
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)
    created_date = db.Column(db.DateTime, default=func.now(), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, current_app.config.get("BCRYPT_LOG_ROUNDS")
        ).decode()

    def to_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "active": self.active,
        }

    def encode_auth_token(self, user_id):
        try:
            payload = {
                "exp": dt.datetime.utcnow()
                + dt.timedelta(
                    days=current_app.config.get("TOKEN_EXPIRATION_DAYS"),
                    seconds=current_app.config.get("TOKEN_EXPIRATION_SECONDS"),
                ),
                "iat": dt.datetime.utcnow(),
                "sub": user_id,
            }
            return jwt.encode(payload, current_app.config.get("SECRET_KEY"), algorithm="HS256")
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        try:
            payload = jwt.decode(
                auth_token, current_app.config.get("SECRET_KEY"), algorithms=["HS256"]
            )
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            return "Signature expired. Log in again"
        except jwt.InvalidTokenError:
            return "Invalid token. Log in again"

