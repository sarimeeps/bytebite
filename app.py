from flask import Flask, render_template, jsonify, request, redirect
from dotenv import load_dotenv
import os
import requests
import psycopg

# please make a python file name db_secrets.py 
# and save database password as DB_PASS


load_dotenv()

app = Flask(__name__)

# Page Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login')
def login():
    
    return render_template('login.html')

@app.get('/register')
def register():
    return render_template('register.html')

@app.route('/calculator')
def calculator():
    return render_template('calculator.html')

@app.route('/builder')
def builder():
    user_id = session.get('user')

    

    return render_template('builder.html')

@app.post('/meal')
def create_meal():
    
    name = request.form['name']
    ingredients = request.form['ingredients']
    # CHANGE
    create_meal(name, ingredients)
    return redirect('/builder')

@app.post('/meal/<int:meal_id>/edit')
def edit_meal(meal_id):
    name = request.form['name']
    ingredients = request.form['ingredients']
    # CHANGE
    edit_meal(meal_id, name, ingredients)
    return redirect('/builder')

@app.post('/meal/<int:meal_id>/delete')
def delete_meal(meal_id):
# CHANGE
    delete_meal(meal_id)
    return redirect('/builder')

@app.route('/food')
def food():
    return render_template('food.html')

@app.route('/foodsearch')
def foodsearch():
    return render_template('foodsearch.html')

@app.route('/profile')
def profile():
    # user = 
    profile_picture = 'static/images/default-profile-pic.jpg'
    # meals = get_user_meals(user_id)
    # return meals=meals when repo is done
    return render_template('profile.html', profile_picture=profile_picture)

# Big Api Call 
@app.get('/food-list')
def food_list():
    api_key = os.getenv('API_KEY')
    url = f'https://api.nal.usda.gov/fdc/v1/foods/list?api_key={api_key}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        return jsonify(errMsg = str(e)), 500

if __name__ == '__main__':
    app.run(debug=True)
