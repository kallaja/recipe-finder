from flask import render_template, request, redirect, url_for, Blueprint, flash
from .db_api_responses import obtain_response_from_database, pass_response_to_database
from .auth_db import register_check_if_user_exists, login_check_if_user_exists
from .api import search_recipe, get_random_recipes
import json
from .forms import RegisterForm, LoginForm
from flask_login import current_user, logout_user, login_required
from . import login_manager
from .models import (User, Recipe, sqlalchemy_db, is_recipe_saved_by_user, save_recipe_for_current_user,
                     unsave_recipe_for_current_user)
from werkzeug.wrappers import Response
from typing import Tuple

with open('data.json', 'r') as file:
    json_data = json.load(file)

main_bp = Blueprint('main', __name__, template_folder='templates', static_folder='static')
auth_bp = Blueprint('auth', __name__, template_folder='templates', static_folder='static')


@main_bp.errorhandler(500)
def internal_error(error):
    return render_template('error500.html'), 500


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def return_recipe_details(response: list, i: int, unique_name: str) \
        -> Tuple[str, str, list, list]:
    """
    Extracts recipe details from the API response.
    :return: dish_name, dish_photo, instructions, ingredients
    """
    dish_name = response[i]['title']
    # check if image available for this recipe
    if 'image' in response[i].keys():
        dish_photo = response[i]['image']
    else:
        dish_photo = None

    instructions = []
    if len(response[i]['analyzedInstructions']) > 0:
        for instruction in response[i]['analyzedInstructions'][0]['steps']:
            instructions.append(instruction)

    # different responses for different spoonacular searching endpoints
    if unique_name in ['2', '4']:
        ingredients = []
        for ingredient in response[i]['extendedIngredients']:
            ingredients.append(ingredient['original'])
        return dish_name, dish_photo, instructions, ingredients
    else:
        ingredients = []
        if len(response[i]['analyzedInstructions']) > 0:
            for step in response[i]['analyzedInstructions'][0]['steps']:
                for ingredient in step['ingredients']:
                    ingredients.append(ingredient['name'])
        return dish_name, dish_photo, instructions, ingredients


def fetch_dish_details_and_render_site(unique_name: str, i: int = 0):
    """
    Fetches dish details from the database and renders the details page.
    Returns:
        i: number of recipe in response.json()['recipes']
    """
    response = obtain_response_from_database(unique_name)

    if response is not None:
        dish_name = response[i]['title']
        recipe_id = Recipe.get_id_by_name(dish_name)
        if recipe_id is not None:  # recipe saved in database
            recipe_saved_by_user = is_recipe_saved_by_user(recipe_id)
        else:
            recipe_saved_by_user = False

        dish_name, dish_photo, instructions, ingredients = return_recipe_details(response, i, unique_name)
        return render_template('dishDetails.html', dish_name=dish_name, dish_photo=dish_photo,
                               instructions=instructions, ingredients=ingredients,
                               unique_name=unique_name, id_num=i, recipe_saved_by_user=recipe_saved_by_user)
    else:
        return redirect(url_for('main.error'))


def capture_searched_data() -> Response:
    """Captures data from the "search" field in the navbar and manage it."""
    searched_dish_name = request.form.get('search')

    response = search_recipe(dish_name=searched_dish_name)
    if response != 1:
        unique_name = '1'
        new_json_data = response.json()['results']
        pass_response_to_database(unique_name, new_json_data)
        # redirect to a page with a list of recipes matching the searched term
        return redirect(url_for('main.searching_results', unique_name=unique_name))
    else:
        return redirect(url_for('main.error', dish_name=searched_dish_name))

# MAIN_BP ------------------------------------------------------------------------------------------------------------


@main_bp.route("/", methods=['GET', 'POST'])
def start():
    """Home page displaying random recipes."""
    if request.method == 'POST' and 'search' in request.form:
        return capture_searched_data()
    elif request.method == 'GET':
        response = get_random_recipes(num_recipes=12)

        unique_name = '2'
        new_json_data = response.json()['recipes']
        pass_response_to_database(unique_name, new_json_data)

        return render_template('start.html',
                               response_results=response.json()['recipes'],
                               unique_name=unique_name)


@main_bp.route('/chooseFilter', methods=['GET', 'POST'])
def choose_filter():
    if request.method == 'POST' and 'search' in request.form:
        return capture_searched_data()
    if request.method == 'POST' and 'searching filter' in request.form:
        selected_filter = request.form.get('searching filter')
        if selected_filter:
            return redirect(url_for('main.preferences', filter_type=selected_filter))
    return render_template('chooseFilter.html')


@main_bp.route('/preferences', methods=['GET', 'POST'])
def preferences():
    if request.method == 'POST' and 'search' in request.form:
        return capture_searched_data()
    elif request.method == 'POST' and "checkBox" in request.form:
        preferences_checked = request.form.getlist('checkBox')

        type_value = request.form.get('type')

        # search for recipes, take filters into account
        if type_value == '1':
            response = search_recipe(user_intolerances=preferences_checked)
        elif type_value == '2':
            response = search_recipe(cuisine_type=preferences_checked)
        else:
            response = search_recipe(diet_type=preferences_checked)

        if response != '1':
            # Store response in database, using a unique key
            unique_name = '3'
            new_json_data = response.json()['results']
            pass_response_to_database(unique_name, new_json_data)

            return redirect(url_for('main.searching_results', unique_name=unique_name))
        else:
            return redirect(url_for('main.error'))

    filter_type = request.args.get('filter_type')
    if filter_type == '1':
        filter_name = 'Intolerances'
        filter_params = json_data['INTOLERANCES_PARAMETERS']
    elif filter_type == '2':
        filter_name = 'Cuisine Type'
        filter_params = json_data['CUISINES_LIST']
    else:
        filter_name = 'Diet Type'
        filter_params = json_data['DIETS_LIST']
    return render_template('preferences.html', filter_params=filter_params, filter_name=filter_name, type=filter_type)


@main_bp.route('/dishDetails/<int:id_num>/<unique_name>', methods=['GET', 'POST'])
def details(id_num: int, unique_name: str):
    if request.method == 'POST' and 'search' in request.form:
        return capture_searched_data()
    return fetch_dish_details_and_render_site(unique_name=unique_name, i=id_num)


@main_bp.route('/random', methods=['GET', 'POST'])
def random():
    if request.method == 'POST' and 'search' in request.form:
        return capture_searched_data()
    response = get_random_recipes(num_recipes=1)
    if response != 1:
        unique_name = '4'
        new_json_data = response.json()['recipes']
        pass_response_to_database(unique_name, new_json_data)
        return fetch_dish_details_and_render_site(unique_name=unique_name, i=0)


@main_bp.route('/searchingResults', methods=['GET', 'POST'])
def searching_results():
    if request.method == 'POST' and 'search' in request.form:
        return capture_searched_data()

    unique_name = request.args.get('unique_name')
    response_results = obtain_response_from_database(unique_name)

    if response_results is not None:
        num_cards = 12
        if len(response_results) < 12:
            num_cards = len(response_results)
        return render_template('searchingResults.html',
                               response_results=response_results, unique_name=unique_name, num_cards=num_cards)
    else:
        redirect(url_for('main.error'))


@main_bp.route('/error', methods=['GET', 'POST'])
def error():
    if request.method == 'POST' and 'search' in request.form:
        return capture_searched_data()
    # fetch "searched_phrase" after using redirect() function
    searched_phrase = request.args.get('dish_name')
    return render_template('error.html', searched_phrase=searched_phrase)


# auth_bp -------------------------------------------------------------------------------------------------------------

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration."""
    register_form = RegisterForm()

    if request.method == 'POST' and 'search' in request.form:
        return capture_searched_data()

    elif register_form.validate_on_submit():
        user_exists = register_check_if_user_exists(form=register_form)
        if user_exists == 1:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('auth.login'))
        elif user_exists == 0:
            return redirect(url_for("main.start"))
        elif user_exists == 2:
            flash("Registration failed, please try again.")
            return redirect(url_for("auth.register"))
    return render_template('register.html', form=register_form, current_user=current_user)


@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    """Handles user login."""
    login_form = LoginForm()

    if request.method == 'POST' and 'search' in request.form:
        return capture_searched_data()

    elif login_form.validate_on_submit():
        if_user_logged = login_check_if_user_exists(login_form)

        if if_user_logged == 1:
            flash("That email does not exist, please try again.")
            return redirect(url_for('auth.login'))
        # Password incorrect
        elif if_user_logged == 2:
            flash('Password incorrect, please try again.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.start'))
    return render_template("login.html", form=login_form, current_user=current_user)


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """Handles user logout."""
    logout_user()
    return redirect(url_for('main.start'))


@main_bp.route('/saveRecipe/<unique_name>/<int:recipe_number>', methods=['POST'])
@main_bp.route('/saveRecipe/<dish_name>', methods=['POST'])
@login_required
def save_recipe(unique_name=None, recipe_number=None, dish_name=None):
    if request.method == 'POST' and 'search' in request.form:
        return capture_searched_data()

    # if recipe_number is None --> recipe is already saved in database (Recipe) -- redirected from savedDishDetails.html
    if recipe_number is None and unique_name is None and dish_name:
        # Retrieve dish details straight from database - Recipe
        recipe_id = Recipe.get_id_by_name(dish_name)
        recipe = Recipe.query.get_or_404(recipe_id)
        # Save recipe in current_user saved_recipes
        # Check if the recipe is already saved
        if recipe not in current_user.saved:
            # Save recipe in current user's saved
            save_recipe_for_current_user(recipe)
        # Redirect back to the recipe page
        return redirect(request.referrer)
    # recipe can be or not saved in database (Recipe)
    elif (unique_name and recipe_number) or unique_name:  # recipe number can be a zero (0)
        # Retrieve the data from the database using unique name
        response_results = obtain_response_from_database(unique_name)

        if response_results is not None:
            dish_name, dish_photo, instructions, ingredients = (
                return_recipe_details(response=response_results, i=recipe_number, unique_name=unique_name))
            # look for this dish in the database (Recipe)
            recipe_id = Recipe.get_id_by_name(dish_name)
            if recipe_id is None:
                # no dish with this name found in the database -- add recipe with this recipe_name to database
                new_recipe = Recipe.add_new_recipe(dish_name=dish_name, dish_photo=dish_photo,
                                                   instructions=json.dumps(instructions),
                                                   ingredients=json.dumps(ingredients))
                recipe_id = new_recipe.id
            # Retrieve the recipe by ID
            recipe = Recipe.query.get_or_404(recipe_id)

            # Check if the recipe is already saved in current user's saved -- if not - save it there
            if recipe not in current_user.saved:
                # Save recipe in current user's saved
                save_recipe_for_current_user(recipe)
            # Redirect back to the recipe page
            return redirect(request.referrer)
        else:
            return redirect(request.referrer)
    else:
        return redirect(request.referrer)


@main_bp.route('/unsaveRecipe/<dish_name>', methods=['POST'])
@login_required
def unsave_recipe(dish_name):
    if request.method == 'POST' and 'search' in request.form:
        return capture_searched_data()

    # recipe was saved by someone, so it is in database for sure
    if dish_name:
        recipe_id = Recipe.get_id_by_name(dish_name)
        # Find the recipe with recipe_id
        recipe = Recipe.query.get(recipe_id)

        # Check if the recipe exists and is in the current user's saved recipes
        if recipe in current_user.saved:
            try:
                # Remove the recipe from the user's saved recipes
                unsave_recipe_for_current_user(recipe)
            except Exception:
                # Rollback in case of any error
                sqlalchemy_db.session.rollback()
        # Redirect back
        return redirect(request.referrer)


@main_bp.route('/savedDishDetails/<int:recipe_id>', methods=['GET', 'POST'])
@login_required
def saved_dish_details(recipe_id):
    if request.method == 'POST' and 'search' in request.form:
        return capture_searched_data()

    # Query to check if the recipe is in the current user's saved recipes
    saved_recipe = current_user.saved.filter_by(id=recipe_id).first()

    # Check if the recipe exists in the saved list
    if saved_recipe:
        dish_name = saved_recipe.dish_name
        dish_photo = saved_recipe.dish_photo
        ingredients = []
        for ingredient in json.loads(saved_recipe.ingredients):
            ingredients.append(ingredient)
        instructions = []
        for instruction in json.loads(saved_recipe.instructions):
            instructions.append(instruction)
        return render_template('savedDishDetails.html', dish_name=dish_name, dish_photo=dish_photo,
                               instructions=instructions, ingredients=ingredients)
    else:
        return redirect(url_for('main.saved_recipes'))


@main_bp.route('/savedRecipes', methods=['GET', 'POST'])
@login_required
def saved_recipes():
    """Renders a page with recipes saved by the user."""
    if request.method == 'POST' and 'search' in request.form:
        return capture_searched_data()

    users_saved_recipes = current_user.saved.all()
    return render_template('savedRecipes.html', recipes=users_saved_recipes)
