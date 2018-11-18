from project import db
from project.api.models import User


def add_user(username, email, password):
    user = User(username, email, password)
    db.session.add(user)
    db.session.commit()
    return user
