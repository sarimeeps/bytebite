from flask import Flask, render_template, jsonify, session
from dotenv import load_dotenv
import os
import requests

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

@app.route('/food')
def food():
    return render_template('food.html')

@app.route('/foodsearch')
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
