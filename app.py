# Importing libraries and modules
from flask import Flask, render_template, jsonify, request, redirect
from dotenv import load_dotenv
import os
import requests
import psycopg


# load enviroment varibles from .env file that contains sensitive data
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Page Routes
# Route for homepage
@app.route('/')
def index():
    return render_template('index.html') # renders homepage

# Route for about page which info about app and developers
@app.route('/about')
def about():
    return render_template('about.html')

# Route for logging in 
@app.route('/login')
def login():
    
    return render_template('login.html')

# Route for registering new users
@app.get('/register')
def register():
    return render_template('register.html')

# Route for nutrition calculator
@app.route('/calculator')
def calculator():
    return render_template('calculator.html')

# Route for builder page
@app.route('/builder')
def builder():
    # user_id = session.get('user')

    

    return render_template('builder.html')

# Route for new meal creation
@app.post('/meal')
def create_meal():
    # gets the form data from user
    name = request.form['name']
    ingredients = request.form['ingredients']
    # CHANGE
    # adds user information to database
    create_meal(name, ingredients)
    return redirect('/builder')

# Route for editing a existing meal
@app.post('/meal/<int:meal_id>/edit')
def edit_meal(meal_id):
    # gets the form data from user
    name = request.form['name']
    ingredients = request.form['ingredients']
    # CHANGE
    # edits the current meal in database
    edit_meal(meal_id, name, ingredients)
    return redirect('/builder')

# route for meal deletion
@app.post('/meal/<int:meal_id>/delete')
def delete_meal(meal_id):
# CHANGE
    # deletes existing meal
    delete_meal(meal_id)
    return redirect('/builder')

# Route for the food page
@app.route('/food')
def food():
    return render_template('food.html')

# Route for food search page
@app.route('/foodsearch')
def foodsearch():
    return render_template('foodsearch.html')

# Route for profile page
@app.route('/profile')
def profile():
    # user = 
    # loads default profile picture for the time being
    profile_picture = 'static/images/default-profile-pic.jpg'
    # meals = get_user_meals(user_id)
    # return meals=meals when repo is done
    return render_template('profile.html', profile_picture=profile_picture)

# Big Api Call 
# USDA FoodData Central
@app.get('/food-list')
def food_list():
    api_key = os.getenv('API_KEY')
    url = f'https://api.nal.usda.gov/fdc/v1/foods/list?api_key={api_key}'

    try:
        # Get request for the API
        response = requests.get(url)
        response.raise_for_status()
        data = response.json() # store API response in JSON
        return data
    except requests.exceptions.RequestException as e:
        # if theres an error with the request, an error message will be returned
        return jsonify(errMsg = str(e)), 500

# Starts the Flask application in debug mode
if __name__ == '__main__':
    app.run(debug=True)
