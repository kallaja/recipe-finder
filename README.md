
# RECIPE-FINDER

## 🌐 LIVE-DEMO
The application is available online at:  
🔗 recipe-finder on Render: (https://recipe-finder-oyox.onrender.com/)  
> Note: The first launch may take longer due to the free Render server going to sleep.

## ⚠️ RESTRICTIONS
The application uses an external API that has a daily query limit. After exceeding this limit, the website may return an error informing about the use of available queries.

## 📊 DATA SOURCE (API)
The app uses spoonacular (https://spoonacular.com/food-api) to download recipes.

## 🚀 CONTENT - FEATURES
✅ On the home page you will see a carousel with various functionalities such as randomizing a recipe or filtering recipes according to your needs, and underneath randomly selected recipes that may be of interest to you.  
✅ Click the "More details" button under the dish photo to see the recipe.    
✅ Log in to take full advantage of the application's functionality. If you have an account, you can save your favorite recipes by clicking the heart so that you can return to them at any time. The list of your saved recipes can be found in the "Saved recipes" tab.  
✅ If you have any special preferences or food intolerances, click the "Filter recipes" tab to sort recipes by: diet type, cuisine type or intolerances.  
✅ You can also search for your favorite dish in the "Search" box in the upper right corner.

## 🛠️ TECHNOLOGIES
The project uses the following technologies:  
Backend: Python, Flask, Flask-Login, Flask-WTF, Werkzeug  
Frontend: HTML, CSS, Flask-Bootstrap, Jinja  
Database: SQLite + SQLAlchemy (ORM)  
Others: Selenium, Requests, Gunicorn
