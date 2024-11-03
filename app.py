from flask import Flask, render_template, jsonify, request, redirect, session, url_for
import os, re
import requests
from flask_bcrypt import Bcrypt
from repositories import user_repository, meal_repository
from dotenv import load_dotenv

# load enviroment varibles from .env file that contains sensitive data
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

bcrypt = Bcrypt(app)

appConfig = {
    "FLASK SECRET": os.getenv('SECRET_KEY')
}

app.secret_key = appConfig["FLASK SECRET"]

email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$'

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
        return render_template('login.html', error=error, username=username)
    
    user = user_repository.get_user_by_username(username)

    if user is None:
        error = "User does not exist."
        return render_template('login.html', error=error, username=username)

    if not bcrypt.check_password_hash(user['password'], password):
        error = "Incorrect password, try again."
        return render_template('login.html', error=error)

    session['user'] = user['username']
    return redirect(url_for('index'))

@app.get('/register')
def register_page():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_user():
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if not re.match(email_regex, email):
        error = "Please use a valid email address."
        return render_template('register.html', error=error, email=email, username=username, password=password)

    if user_repository.get_user_by_email(email):
        error = "Email is already registered."
        return render_template('register.html', error=error, username=username, password=password)

    if user_repository.get_user_by_username(username):
        error = "Username is already taken."
        return render_template('register.html', error=error, email=email, password=password)
    
    if password != confirm_password:
        error = "Passwords do not match."
        return render_template('register.html', error=error, email=email, username=username, password=password)

    if not re.match(password_regex, password):
        error = "Password must contain at least 12 characters including uppercase, lowercase, number, and special character."
        return render_template('register.html', error=error, email=email, username=username, password=password)

    if not all([email, username, password, confirm_password]):
        error = "All fields are required."
        return render_template('register.html', error=error, email=email, username=username, password=password)
    
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    user_repository.create_user(email, username, hashed_password)

    return redirect(url_for('login_page'))

@app.get('/calculator')
def calculator():
    return render_template('calculator.html')

@app.get('/builder')
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

@app.get('/food')
def food():
    return render_template('food.html')


# FUNCTION FOR SEARCHING A FOOD ITEM
@app.post('/foodsearch/')
def foodsearch():
 
    query = request.form.get("query")

    api_key = os.getenv('API_KEY')
    url = f'https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={query}&pageSize={10}'
    print(query)
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        foods = data["foods"]
        return render_template('foodsearch.html', foods=foods)
    except requests.exceptions.RequestException as e:
        return jsonify(errMsg = str(e)), 500

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
        print(data)
        return data
    except requests.exceptions.RequestException as e:
        # if theres an error with the request, an error message will be returned
        return jsonify(errMsg = str(e)), 500
    
    
#Returns Information on a specific food item. 
#Food's fdcId is a required route parameter
@app.get('/food/<id>')
def food_info(id):
    api_key = os.getenv('API_KEY')
    url = f'https://api.nal.usda.gov/fdc/v1/food/{id}?api_key={api_key}'
    
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        return jsonify(data=data)
    except requests.exceptions.RequestException as e:
        return jsonify(errMsg = str(e)), 500
    


# Starts the Flask application in debug mode
if __name__ == '__main__':
    app.run(debug=True)
