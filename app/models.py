from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, Table, Column, JSON
from flask_login import UserMixin, current_user


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass


# delay import
from .extensions import sqlalchemy_db


# Association Table (User - Recipe)
saved_recipes = Table(
    'saved_recipes',
    sqlalchemy_db.Model.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('recipe_id', Integer, ForeignKey('recipes.id'), primary_key=True)
)


class User(UserMixin, sqlalchemy_db.Model):
    """User model for storing user-related data."""
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))

    # Many-to-Many Relationship: User <-> Saved Recipes
    saved: Mapped[list['Recipe']] = relationship(
        'Recipe',
        secondary=saved_recipes,
        back_populates='saved_by',
        lazy='dynamic'
    )

    def __init__(self, email, password, name):
        super().__init__()
        self.email = email
        self.password = password
        self.name = name


class Recipe(sqlalchemy_db.Model):
    """Recipe model representing a saved recipe."""
    __tablename__ = 'recipes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dish_name: Mapped[String] = mapped_column(String, nullable=False, unique=True)
    dish_photo: Mapped[String] = mapped_column(String, nullable=True)
    instructions: Mapped[JSON] = mapped_column(JSON, nullable=False)
    ingredients: Mapped[JSON] = mapped_column(JSON, nullable=False)

    # Many-to-Many Relationship: Recipe <-> Saved by Users
    saved_by: Mapped[list['User']] = relationship(
        'User',
        secondary=saved_recipes,
        back_populates='saved',
        lazy='dynamic'
    )

    @classmethod
    def get_id_by_name(cls, name: str) -> int | None:
        """Retrieves recipe id from database by name (if exists)."""
        recipe = cls.query.filter_by(dish_name=name).first()
        return recipe.id if recipe else None

    @classmethod
    def add_new_recipe(cls, dish_name: str, dish_photo: str, instructions: JSON | str, ingredients: JSON | str) \
            -> 'Recipe':
        """Adds a new recipe to the database."""
        new_recipe = cls(
            dish_name=dish_name,
            dish_photo=dish_photo,
            instructions=instructions,
            ingredients=ingredients,
        )
        sqlalchemy_db.session.add(new_recipe)
        sqlalchemy_db.session.commit()
        return new_recipe


def is_recipe_saved_by_user(recipe_id: int) -> bool:
    """
    Checks if the recipe is saved by the current user.
    :return: True: recipe is saved by the current user,
        False: recipe isn't saved by the current user
    """
    return bool(current_user.saved.filter_by(id=recipe_id).first())


def save_recipe_for_current_user(recipe: 'Recipe') -> None:
    """Adds a recipe to the current user's saved recipes."""
    if not current_user.saved.filter_by(id=recipe.id).first():
        current_user.saved.append(recipe)
        sqlalchemy_db.session.commit()


def unsave_recipe_for_current_user(recipe: 'Recipe') -> None:
    """Removes a recipe from the current user's saved recipes."""
    if current_user.saved.filter_by(id=recipe.id).first():
        current_user.saved.remove(recipe)
        sqlalchemy_db.session.commit()
