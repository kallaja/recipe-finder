from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, Table, Column, JSON
from flask_login import UserMixin, current_user


class Base(DeclarativeBase):
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


# Create a User table for all your registered users
class User(UserMixin, sqlalchemy_db.Model):
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
        super().__init__()  # Initialize UserMixin
        self.email = email
        self.password = password
        self.name = name


class Recipe(sqlalchemy_db.Model):
    __tablename__ = 'recipes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dish_name: Mapped[String] = mapped_column(String, nullable=False, unique=True)
    dish_photo: Mapped[String] = mapped_column(String, nullable=False)
    instructions: Mapped[JSON] = mapped_column(JSON, nullable=False)
    ingredients: Mapped[JSON] = mapped_column(JSON, nullable=False)

    # Many-to-Many Relationship: Recipe <-> Saved by Users
    saved_by: Mapped[list['User']] = relationship(
        'User',
        secondary=saved_recipes,
        back_populates='saved',
        lazy='dynamic'
    )

    # Class method to get recipe ID by title
    @classmethod
    def get_id_by_name(cls, name: str) -> int | None:
        recipe = cls.query.filter_by(dish_name=name).first()
        return recipe.id if recipe else None

    # Class method to add a new recipe
    @classmethod
    def add_new_recipe(cls, dish_name: str, dish_photo: str, instructions: JSON | str, ingredients: JSON | str) \
            -> 'Recipe':
        # Create a new recipe object
        new_recipe = cls(
            dish_name=dish_name,
            dish_photo=dish_photo,
            instructions=instructions,
            ingredients=ingredients,
        )
        # Add the new recipe to the session
        sqlalchemy_db.session.add(new_recipe)
        sqlalchemy_db.session.commit()  # Commit the session to save the new recipe in the database
        return new_recipe


# functions -------------------------------------------------------------------------------------------------------
def is_recipe_saved_by_user(recipe_id: int) -> bool:
    # Query the saved recipes of the current user to check if the recipe with the given id exists there
    saved_recipe = current_user.saved.filter_by(id=recipe_id).first()

    # Check if the recipe exists in the current_user.saved
    if saved_recipe:
        return True  # Recipe is saved by the current user
    return False  # Recipe is not saved by the current user
