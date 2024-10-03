from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user
from .models import User
from .extensions import sqlalchemy_db

# DATABASE FOR AUTHORIZING USERS ------------------------------------


def add_user(email, password, name):
    # Create a new session
    session = sqlalchemy_db.session
    # Hash a password with the given method and salt with a string of the given length
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


# Check if user email is already present in the database.
# return 1 - user with this email exists, return 0 - no user with this email
def register_check_if_user_exists(form):
    # Create a new session
    session = sqlalchemy_db.session

    result = session.execute(sqlalchemy_db.select(User).where(User.email == form.email.data))
    user = result.scalar()
    if user:
        # User already exists
        return 1

    new_user = add_user(email=form.email.data, password=form.password.data, name=form.name.data)
    # This line will authenticate the user with Flask-Login
    login_user(new_user)
    return 0


# return 1 - user with this email doesn't exist
# return 2 - password incorrect (but user with this email exists)
# return 0 - email and password correct - user logged
def login_check_if_user_exists(form):
    # Create a new session
    session = sqlalchemy_db.session

    # check if user with this email exists in database
    result = session.execute(sqlalchemy_db.select(User).where(User.email == form.email.data))
    # Note, email in db is unique so will only have one result.
    user = result.scalar()
    # Email doesn't exist
    if not user:
        return 1
    # Password incorrect
    elif not check_password_hash(user.password, form.password.data):
        return 2
    else:
        login_user(user)
        return 0
