from .config import Config
import requests
import json
from werkzeug.exceptions import InternalServerError

with open('data.json', 'r') as file:
    json_data = json.load(file)


def search_recipe(dish_name: str = None, user_intolerances: list[str] = None, cuisine_type: list[str] = None,
                  diet_type: list[str] = None) -> requests.models.Response | int:
    """
    Queries the spoonacular API for the recipe, taking into account the user's preferences.
    :return: requests.Response | int: API response if recipes are found, otherwise 1.
    """
    endpoint = 'https://api.spoonacular.com/recipes/complexSearch'

    header = {'x-api-key': Config.API_KEY}
    data = {'sort': 'popularity',
            'number': 12,
            'instructionsRequired': 'true',
            'addRecipeInstructions': 'true',
            'addRecipeNutrition': 'true'
            }

    # Add all user's preferences to 'data':
    if dish_name is not None:
        data['query'] = dish_name

    if user_intolerances is not None:
        for parameter in json_data['INTOLERANCES_PARAMETERS']:
            if parameter in user_intolerances:
                data[f'{parameter}'] = 'true'
            else:
                data[f'{parameter}'] = 'false'

    if cuisine_type is not None:
        string = ','.join(cuisine_type)
        data['cuisine'] = string

    if diet_type is not None:
        string = ','.join(diet_type)
        data['diet'] = string

    response = requests.get(url=endpoint, headers=header, params=data)

    try:
        if len(response.json()['results']) > 0:
            return response
        else:
            return 1
    except KeyError:
        raise InternalServerError("Missing 'results' key in API response.")


def get_random_recipes(num_recipes: int) -> requests.models.Response | int:
    """
    Fetches a given number of random recipes.

    Args:
        num_recipes (int): The number of random recipes to fetch.
    Returns:
        requests.Response | int: API response if recipes are found, otherwise 1.
    """
    endpoint = 'https://api.spoonacular.com/recipes/random'

    header = {'x-api-key': Config.API_KEY}
    data = {'number': num_recipes}

    response = requests.get(url=endpoint, headers=header, params=data)

    try:
        if len(response.json()['recipes']) > 0:
            return response
        else:
            return 1
    except KeyError:
        raise InternalServerError("Key 'recipes' is missing")
