from flask import Flask, render_template, jsonify, request, redirect, session, url_for
from dotenv import load_dotenv
import os
import requests
import psycopg
from repositories import user_repository, meal_repository


load_dotenv()

app = Flask(__name__)

# Page Routes
@app.get('/')
def index():
    return render_template('index.html')

@app.get('/about')
def about_page():
    return render_template('about.html')

@app.get('/login')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        error = "Please enter a valid username and password."
        return render_template('login.html', error=error)
    
    user = user_repository.get_user_by_username(username)

    if user is None:
        error = "User does not exist."
        return render_template('login.html', error=error)

    if user['password'] != password:
        error = "Incorrect password, try again!"
        return render_template('login.html', error=error)

    session['user'] = user['username']
    return redirect(url_for('index'))

@app.get('/register')
def register():
    return render_template('register.html')

@app.get('/calculator')
def calculator():
    return render_template('calculator.html')

@app.get('/builder')
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

@app.get('/food')
def food():
    return render_template('food.html')

@app.get('/foodsearch')
def foodsearch():
    return render_template('foodsearch.html')

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
