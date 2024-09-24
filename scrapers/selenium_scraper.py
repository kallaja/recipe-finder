import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By

# Get the user's home directory
user_profile = os.path.expanduser('~')

endpoint_intolerances = 'https://spoonacular.com/food-api/docs#Intolerances'
intolerances_xpath = '/html/body/div[1]/div/div/div/section[111]/ul/li'

endpoint_cuisines = 'https://spoonacular.com/food-api/docs#Cuisines'
cuisines_xpath = '/html/body/div[1]/div/div/div/section[114]/ul/li'

endpoint_diets = 'https://spoonacular.com/food-api/docs#Diets'
diets_xpath = '/html/body/div[1]/div/div/div/section[117]/h4'


def webscraper(endpoint, xpath):
    # open Chrome browser
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument(
        r"user-data-dir=" + os.path.join(user_profile, "AppData", "Local", "Google", "Chrome", "User Data"))
    chrome_options.add_argument(r'--profile-directory=Profile 1')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(endpoint)

    # scrape potentially intolerable ingredients off the page
    elements = driver.find_elements(By.XPATH, xpath)

    # add text content from selenium elements to the "params_list"
    params_list = []
    for element in elements:
        params_list.append(element.text)

    # close the browser window
    driver.quit()
    return params_list


# call function, which scrape parameters off the page
INTOLERANCES_PARAMETERS = webscraper(endpoint=endpoint_intolerances, xpath=intolerances_xpath)
CUISINES_LIST = webscraper(endpoint=endpoint_cuisines, xpath=cuisines_xpath)
DIETS_LIST = webscraper(endpoint=endpoint_diets, xpath=diets_xpath)

dictionary = {
    'INTOLERANCES_PARAMETERS': INTOLERANCES_PARAMETERS,
    'CUISINES_LIST': CUISINES_LIST,
    'DIETS_LIST': DIETS_LIST
}

with open('../data.json', 'w') as file:
    json.dump(dictionary, file, indent=4)