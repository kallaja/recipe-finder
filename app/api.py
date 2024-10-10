from .config import Config
import requests
import json
from werkzeug.exceptions import InternalServerError

with open('../data.json', 'r') as file:
    json_data = json.load(file)


def search_recipe(dish_name: str = None, user_intolerances: list[str] = None, cuisine_type: list[str] = None,
                  diet_type: list[str] = None) -> requests.models.Response | int:
    endpoint = 'https://api.spoonacular.com/recipes/complexSearch'

    header = {'x-api-key': Config.API_KEY}
    data = {'sort': 'popularity',
            'number': 12,
            'instructionsRequired': 'true',
            # 'addRecipeInformation': 'true',
            'addRecipeInstructions': 'true',
            'addRecipeNutrition': 'true'
            }
    # if the variable "dish_name" was passed as an argument --> add to data
    if dish_name is not None:
        data['query'] = dish_name

    # add information about intolerances to the "data"
    if user_intolerances is not None:
        # check which from all intolerances was selected by user
        for parameter in json_data['INTOLERANCES_PARAMETERS']:
            if parameter in user_intolerances:
                # add intolerances to data as true
                data[f'{parameter}'] = 'true'
            else:
                data[f'{parameter}'] = 'false'

    # add preferences about cuisine to the "data"
    if cuisine_type is not None:
        # connect elements from a list into a string (elements seperated by commas)
        string = ','.join(cuisine_type)
        data['cuisine'] = string

    # add preferences about diet type to the "data"
    if diet_type is not None:
        string = ','.join(diet_type)
        data['diet'] = string

    # get recipies (searching based on filters in 'data')
    response = requests.get(url=endpoint, headers=header, params=data)

    # return response if the dishes were found or 1 when no dish found
    try:
        if len(response.json()['results']) > 0:
            return response
        else:
            return 1
    except KeyError:
        raise InternalServerError("Key 'results' is missing")


def get_random_recipes(num_recipes: int) -> requests.models.Response | int:
    endpoint = 'https://api.spoonacular.com/recipes/random'

    header = {'x-api-key': Config.API_KEY}
    data = {'number': num_recipes}

    response = requests.get(url=endpoint, headers=header, params=data)

    # check if the dish the user was looking for has been found
    try:
        if len(response.json()['recipes']) > 0:
            return response
        else:
            return 1
    except KeyError:
        raise InternalServerError("Key 'recipes' is missing")
