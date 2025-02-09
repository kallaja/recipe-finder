from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user
from .models import User
from .extensions import sqlalchemy_db
from sqlalchemy.exc import IntegrityError


def add_user(email, password, name) -> User | None:
    """Creates a new user and stores it in the database."""
    session = sqlalchemy_db.session
    try:
        hash_and_salted_password = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=email,
            name=name,
            password=hash_and_salted_password
        )
        session.add(new_user)
        session.commit()
        return new_user
    except IntegrityError:
        session.rollback()
        print(f"Error: User with email {email} already exists.")
        return None
    except Exception as e:
        session.rollback()
        print(f"Unexpected error: {e}")
        return None


def register_check_if_user_exists(form) -> int:
    """
    Adds a new user if no user with this email address already exists.
    :return:  1 - User already exists,
        0 - User does not exist and is registered successfully
        2 - User does not exist and registration has failed
    """
    session = sqlalchemy_db.session
    result = session.execute(sqlalchemy_db.select(User).where(User.email == form.email.data))
    user = result.scalar()

    if user:
        return 1
    new_user = add_user(email=form.email.data, password=form.password.data, name=form.name.data)
    if new_user:
        login_user(new_user)
        return 0
    return 2


def login_check_if_user_exists(form) -> int:
    """
    Logs the user in if both email and password are correct.
    :return: 1 - user with this email doesn't exist,
        2 - password incorrect (but user with this email exists),
        0 - email and password correct - successful login
    """
    session = sqlalchemy_db.session
    result = session.execute(sqlalchemy_db.select(User).where(User.email == form.email.data))
    user = result.scalar()
    if not user:
        return 1
    elif not check_password_hash(user.password, form.password.data):
        return 2
    login_user(user)
    return 0
