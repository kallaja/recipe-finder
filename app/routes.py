from flask import render_template, request, redirect, url_for, Blueprint
from .db import obtain_response_from_database, pass_response_to_database
from .api import search_recipe, get_random_recipes
import json

with open('data.json', 'r') as file:
    json_data = json.load(file)

main_bp = Blueprint('main', __name__, template_folder='templates', static_folder='static')


# fetch dish details for the website dedicated to one recipe;
# "i" stands for number of recipe in response.json()['recipes']
def fetch_dish_details_and_render_site(unique_name, i=0):
    # Retrieve the data from the database using unique name
    response = obtain_response_from_database(unique_name)

    if response is not None:
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

            return render_template('dishDetails.html', dish_name=dish_name, dish_photo=dish_photo,
                                   instructions=instructions, ingredients=ingredients, unique_name=unique_name)
        else:
            ingredients = []
            if len(response[i]['analyzedInstructions']) > 0:
                for step in response[i]['analyzedInstructions'][0]['steps']:
                    for ingredient in step['ingredients']:
                        ingredients.append(ingredient['name'])

            return render_template('dishDetails.html', dish_name=dish_name, dish_photo=dish_photo,
                                   instructions=instructions, ingredients=ingredients, unique_name=unique_name)
    else:
        return redirect(url_for('main.error'))


# capture data from the "search" field in the navbar and manage it
def capture_searched_data():
    searched_dish_name = request.form.get('search')  # value to get is from input name

    # look for the dish name entered in navbar search field
    response = search_recipe(dish_name=searched_dish_name)

    # if the dishes were found
    if response != 1:
        # Store response in database, using a unique key
        unique_name = '1'
        new_json_data = response.json()['results']
        pass_response_to_database(unique_name, new_json_data)

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
        searching_filter = request.form.get('searching filter')

        if searching_filter:
            return redirect(url_for('main.preferences', filter_type=searching_filter))

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
def details(id_num, unique_name):
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
