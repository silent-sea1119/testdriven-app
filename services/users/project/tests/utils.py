from project import db
from project.api.models import User


def add_user(username, email):
    user = User(username, email)
    db.session.add(user)
    db.session.commit()
    return user
