from flask import Flask, render_template, jsonify, request, redirect
from dotenv import load_dotenv
import os
import requests
import psycopg

# please make a python file name db_secrets.py 
# and save database password as DB_PASS

#from db_secrets import DB_PASS

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

# API Functions

# Big API Call 
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
    
# Returns Information on a specific food item. 
# Food's fdcId is a required route parameter
# @app.get('/food/<id>')
# def food_info(id):
#     api_key = os.getenv('API_KEY')
#     url = f'https://api.nal.usda.gov/fdc/v1/food/{id}?api_key={api_key}'
    
#     try:
#         res = requests.get(url)
#         res.raise_for_status()
#         data = res.json()
#         return jsonify(data=data)
#     except requests.exceptions.RequestException as e:
#         return jsonify(errMsg = str(e)), 500
    
# Searches a food item by name
# Search query is a required route parameter
@app.get('/search/<query>')
def query_food(query):
    api_key = os.getenv('API_KEY')
    url = f'https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={query}&pageSize={10}'

    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        return jsonify(errMsg = str(e)), 500

# Feature Functionalites

def get_food_info(id):
    api_key = os.getenv('API_KEY')
    url = f'https://api.nal.usda.gov/fdc/v1/food/{id}?api_key={api_key}'
    
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        return data
    except requests.exceptions.RequestException as e:
        return {"errMsg": str(e)}

# Get ingredients of a specific food
@app.get('/food/<id>/ingredients')
def food_ingredients(id):
    data = get_food_info(id)
    if "errMsg" in data:
        return jsonify(data), 500
    
    ingredients = data.get("ingredients")
    if ingredients is None:
        return jsonify(errMsg="Ingredients not found"), 404

    return jsonify(ingredients=ingredients)

if __name__ == '__main__':
    app.run(debug=True)
