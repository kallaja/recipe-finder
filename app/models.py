from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin


class Base(DeclarativeBase):
    pass


# delay import
from .extensions import sqlalchemy_db


# Create a User table for all your registered users
class User(UserMixin, sqlalchemy_db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))

    # If you have a constructor defined, make sure it calls super() properly.
    def __init__(self, email, password, name):
        super().__init__()  # Initialize UserMixin
        self.email = email
        self.password = password
        self.name = name
