from flask import render_template, request, redirect, url_for, Blueprint, flash
from .db import obtain_response_from_database, pass_response_to_database
from .auth_db import register_check_if_user_exists, login_check_if_user_exists
from .api import search_recipe, get_random_recipes
import json
from .forms import RegisterForm, LoginForm
from flask_login import current_user, logout_user, login_required
from . import login_manager
from .models import User, Recipe, sqlalchemy_db, is_recipe_saved_by_user
from werkzeug.wrappers import Response
from typing import Tuple

with open('data.json', 'r') as file:
    json_data = json.load(file)

main_bp = Blueprint('main', __name__, template_folder='templates', static_folder='static')
auth_bp = Blueprint('auth', __name__, template_folder='templates', static_folder='static')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def return_recipe_details(response: list, i: int, unique_name: str) \
        -> Tuple[str, str, list, list]:
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


# fetch dish details for the website dedicated to one recipe;
# "i" stands for number of recipe in response.json()['recipes']
def fetch_dish_details_and_render_site(unique_name: str, i: int = 0) -> Response:
    # Retrieve the data from the database using unique name
    response = obtain_response_from_database(unique_name)

    if response is not None:
        dish_name = response[i]['title']
        # retrieve recipe id from database (if exists)
        recipe_id = Recipe.get_id_by_name(dish_name)
        if recipe_id is not None:  # recipe saved in database
            recipe_saved_by_user = is_recipe_saved_by_user(recipe_id)
            # obtain dish details straight from database
            dish_name, dish_photo, instructions, ingredients = return_recipe_details(response, i, unique_name)
            return render_template('dishDetails.html', dish_name=dish_name, dish_photo=dish_photo,
                                   instructions=instructions, ingredients=ingredients,
                                   unique_name=unique_name, id_num=i, recipe_saved_by_user=recipe_saved_by_user)
        else:
            recipe_saved_by_user = False
        # check if image available for this recipe
        if 'image' in response[i].keys():
            dish_photo = response[i]['image']
        else:
            dish_photo = None

        instructions = []
        if len(response[i]['analyzedInstructions']) > 0:
            for instruction in response[i]['analyzedInstructions'][0]['steps']:
                instructions.append(instruction)

        if unique_name in ['2', '4']:
            ingredients = []
            for ingredient in response[i]['extendedIngredients']:
                ingredients.append(ingredient['original'])
            return render_template('dishDetails.html', dish_name=dish_name, dish_photo=dish_photo,
                                   instructions=instructions, ingredients=ingredients,
                                   unique_name=unique_name, id_num=i, recipe_saved_by_user=recipe_saved_by_user)
        else:
            ingredients = []
            if len(response[i]['analyzedInstructions']) > 0:
                for step in response[i]['analyzedInstructions'][0]['steps']:
                    for ingredient in step['ingredients']:
                        ingredients.append(ingredient['name'])
            return render_template('dishDetails.html', dish_name=dish_name, dish_photo=dish_photo,
                                   instructions=instructions, ingredients=ingredients,
                                   unique_name=unique_name, id_num=i, recipe_saved_by_user=recipe_saved_by_user)
    else:
        return redirect(url_for('main.error'))


# capture data from the "search" field in the navbar and manage it
def capture_searched_data() -> Response:
    searched_dish_name = request.form.get('search')

    # look for the dish name entered in navbar search field
    response = search_recipe(dish_name=searched_dish_name)
    # if the dishes were found
    if response != 1:
        # Store response in database, using a unique key
        unique_name = '1'
        new_json_data = response.json()['results']
        print(new_json_data)
        pass_response_to_database(unique_name, new_json_data)
        # redirect to a page with a list of recipes matching the searched term
        return redirect(url_for('main.searching_results', unique_name=unique_name))
    else:
        return redirect(url_for('main.error', dish_name=searched_dish_name))


@main_bp.route("/", methods=['GET', 'POST'])
def start():
    if request.method == 'POST' and 'search' in request.form:
        # capture data from the "search" field in the navbar and manage it
        return capture_searched_data()
    elif request.method == 'GET':
        # obtain random recipes
        response = get_random_recipes(num_recipes=12)

        # Store response in database, using a unique key
        unique_name = '2'
        new_json_data = response.json()['recipes']
        pass_response_to_database(unique_name, new_json_data)

        return render_template('start.html',
                               response_results=response.json()['recipes'],
                               unique_name=unique_name)


@main_bp.route('/chooseFilter', methods=['GET', 'POST'])
def choose_filter():
    if request.method == 'POST' and 'search' in request.form:
        # capture data from the "search" field in the navbar and manage it
        return capture_searched_data()
    if request.method == 'POST' and 'searching filter' in request.form:
        # fetch data what option was selected in a form
        selected_filter = request.form.get('searching filter')
        if selected_filter:
            return redirect(url_for('main.preferences', filter_type=selected_filter))
    return render_template('chooseFilter.html')


@main_bp.route('/preferences', methods=['GET', 'POST'])
def preferences():
    if request.method == 'POST' and 'search' in request.form:
        # capture data from the "search" field in the navbar and manage it
        return capture_searched_data()
    elif request.method == 'POST' and "checkBox" in request.form:
        preferences_checked = request.form.getlist('checkBox')

        # Get the 'type' argument from the hidden input field
        type_value = request.form.get('type')

        # search for recipes, take filters into account
        if type_value == '1':
            response = search_recipe(user_intolerances=preferences_checked)
        elif type_value == '2':
            response = search_recipe(cuisine_type=preferences_checked)
        else:
            response = search_recipe(diet_type=preferences_checked)

        # if the dishes were found
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
        # capture data from the "search" field in the navbar and manage it
        return capture_searched_data()
    return fetch_dish_details_and_render_site(unique_name=unique_name, i=id_num)


@main_bp.route('/random', methods=['GET', 'POST'])
def random():
    if request.method == 'POST' and 'search' in request.form:
        # capture data from the "search" field in the navbar and manage it
        return capture_searched_data()
    # generate random recipe
    response = get_random_recipes(num_recipes=1)
    # check if the dish the user was looking for has been found
    if response != 1:
        # Store response in database, using a unique key
        unique_name = '4'
        new_json_data = response.json()['recipes']
        pass_response_to_database(unique_name, new_json_data)
        return fetch_dish_details_and_render_site(unique_name=unique_name, i=0)


@main_bp.route('/searchingResults', methods=['GET', 'POST'])
def searching_results():
    if request.method == 'POST' and 'search' in request.form:
        # capture data from the "search" field in the navbar and manage it
        return capture_searched_data()

    # Retrieve the data from the database using unique name
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
        # capture data from the "search" field in the navbar and manage it
        return capture_searched_data()
    # fetch "searched_phrase" after using redirect() function
    searched_phrase = request.args.get('dish_name')
    return render_template('error.html', searched_phrase=searched_phrase)


# auth_bp -------------------------------------------------------------------------------------------------------------

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()

    if request.method == 'POST' and 'search' in request.form:
        # capture data from the "search" field in the navbar and manage it
        return capture_searched_data()
    elif register_form.validate_on_submit():
        # check if user with this email exists in the database, if no -> add
        user_exists = register_check_if_user_exists(form=register_form)
        if user_exists:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for("main.start"))
    return render_template('register.html', form=register_form, current_user=current_user)


@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    login_form = LoginForm()

    if request.method == 'POST' and 'search' in request.form:
        # capture data from the "search" field in the navbar and manage it
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
    logout_user()
    return redirect(url_for('main.start'))


@main_bp.route('/saveRecipe/<unique_name>/<int:recipe_number>', methods=['POST'])
@main_bp.route('/saveRecipe/<dish_name>', methods=['POST'])
@login_required
def save_recipe(unique_name=None, recipe_number=None, dish_name=None):
    if request.method == 'POST' and 'search' in request.form:
        # capture data from the "search" field in the navbar and manage it
        return capture_searched_data()

    # if recipe_number is None --> recipe is saved in database (Recipe) -- redirect from savedDishDetails.html
    if recipe_number is None and unique_name is None and dish_name:
        # Retrieve dish details straight from database - Recipe
        recipe_id = Recipe.get_id_by_name(dish_name)
        recipe = Recipe.query.get_or_404(recipe_id)
        # Save recipe in current_user saved_recipes
        # Check if the recipe is already saved
        if recipe in current_user.saved:
            flash('Recipe already saved.', 'info')
        else:
            # Save recipe in current_user saved
            current_user.saved.append(recipe)
            sqlalchemy_db.session.commit()
            flash('Recipe saved successfully!', 'success')
        # Redirect back to the recipe page
        return redirect(request.referrer)
    elif unique_name and recipe_number:
        # Retrieve the data from the database using unique name
        response_results = obtain_response_from_database(unique_name)

        if response_results is not None:
            dish_name, dish_photo, instructions, ingredients = (
                return_recipe_details(response=response_results, i=recipe_number, unique_name=unique_name))
            recipe_id = Recipe.get_id_by_name(dish_name)
            if recipe_id is None:
                # if no: add recipe with this recipe_name to database
                new_recipe = Recipe.add_new_recipe(dish_name=dish_name, dish_photo=dish_photo,
                                                   instructions=json.dumps(instructions),
                                                   ingredients=json.dumps(ingredients))
                recipe_id = new_recipe.id
            # Retrieve the recipe by ID
            recipe = Recipe.query.get_or_404(recipe_id)

            # Check if the recipe is already saved
            if recipe in current_user.saved:
                flash('Recipe already saved.', 'info')
            else:
                # Save recipe in current_user saved
                current_user.saved.append(recipe)
                sqlalchemy_db.session.commit()
                flash('Recipe saved successfully!', 'success')

            # Redirect back to the recipe page
            return redirect(request.referrer)
        else:
            flash('Recipe not found.')
            return redirect(request.referrer)
    else:
        flash('Recipe not found.')
        return redirect(request.referrer)


@main_bp.route('/unsaveRecipe/<dish_name>', methods=['POST'])
@login_required
def unsave_recipe(dish_name):
    if request.method == 'POST' and 'search' in request.form:
        # capture data from the "search" field in the navbar and manage it
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
                current_user.saved.remove(recipe)
                # Commit the changes to the database
                sqlalchemy_db.session.commit()
            except Exception as e:
                # Rollback in case of any error
                sqlalchemy_db.session.rollback()
                flash('An error occurred while removing the recipe.', 'danger')
        else:
            flash('Recipe not found in your saved recipes.', 'warning')

        # Redirect back
        return redirect(request.referrer)


@main_bp.route('/savedDishDetails/<int:recipe_id>', methods=['GET', 'POST'])
@login_required
def saved_dish_details(recipe_id):
    if request.method == 'POST' and 'search' in request.form:
        # capture data from the "search" field in the navbar and manage it
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
        flash("Can't find this recipe.")
        return redirect(url_for('main.saved_recipes'))


@main_bp.route('/savedRecipes', methods=['GET', 'POST'])
@login_required
def saved_recipes():
    if request.method == 'POST' and 'search' in request.form:
        # capture data from the "search" field in the navbar and manage it
        return capture_searched_data()

    # Retrieve all saved recipes for the currently logged-in user
    users_saved_recipes = current_user.saved.all()
    # pass this list as an argument to render site
    return render_template('savedRecipes.html', recipes=users_saved_recipes)
