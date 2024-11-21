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

recent_searches = []

# Page Routes
@app.get('/')
def index():
    recent = recent_searches
    return render_template('index.html', recent=recent)

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
    session['user_id'] = user['user_id']
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

@app.route('/foodmeal/', methods=['GET', 'POST'])
def foodmeal():
    query = request.form.get("query") if request.method == 'POST' else None
    if query:
        api_key = os.getenv('API_KEY')
        url = f'https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={query}&pageSize={10}'
        print(query)
        try:
            res = requests.get(url)
            res.raise_for_status()
            data = res.json()
            foods = data["foods"]
            return render_template('foodmeal.html', foods=foods)
        except requests.exceptions.RequestException as e:
            return jsonify(errMsg = str(e)), 500
    else:
        return render_template('foodmeal.html', foods=[])

@app.post('/add_to_meal')
def add_to_meal():
    item = {'fdcId' : request.form.get('fdcId'),
            'description' : request.form.get('description')
    }
    meal_items = session.get('meal_items', [])
    meal_items.append(item)
    session['meal_items'] = meal_items
    return redirect(url_for('builder'))  

@app.post('/create_meal')
def create_meal():
    meal_items = session.get('meal_items', [])
    meal_id = session.get('meal_id')

    if meal_id and meal_items:
        for item in meal_items:
            meal_repository.add_food_to_meal(meal_id, item['fdcId'], item['description'])
        # Clear the temporary food items after creating the meal
        session.pop('meal_items', None)
        session.pop('meal_id', None)
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('builder'))

@app.post('/update_meal_name')
def update_meal_name():
    meal_id = session.get('meal_id')
    if not meal_id:
        return redirect(url_for('builder'))  
    meal_name = request.form.get('meal_name')
    meal_repository.update_meal_name(meal_id, meal_name)

    return redirect(url_for('builder'))

@app.route('/builder', methods=['GET', 'POST'])
def builder():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login_page'))

    if request.method == 'POST':
        if 'meal_id' not in session:
            meal_id = meal_repository.create_meal(user_id)
            session['meal_id'] = meal_id
    meal_id = session.get('meal_id')
    meal_items= meal_repository.get_food(meal_id)
    food = session.get('meal_items', [])
    food_count= len(food)

    return render_template('builder.html', meal_items=meal_items, food_count=food_count)



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

# LIST FOR RECENT SEARCHES TO BE DISPLAYED IN INDEX

@app.get('/food/<id>')
def food(id):
    api_key = os.getenv('API_KEY')
    url = f'https://api.nal.usda.gov/fdc/v1/food/{id}?api_key={api_key}'

    nutrient_ids = [1087, 1093, 1104, 1079, 2000, 1004, 1003, 1008, 1175, 1257, 
                    1005, 1092, 1089, 1110, 1253, 1293]
    

    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        food_name = data["description"]

        food_info = [nutrient for nutrient in data["foodNutrients"] 
                     if nutrient["nutrient"]["id"] in nutrient_ids]

        protein_info = next((nutrient for nutrient in food_info if nutrient["nutrient"]["id"] == 1003), None)
        fiber_info = next((nutrient for nutrient in food_info if nutrient["nutrient"]["id"] == 1079), None)
        calorie_info = next((nutrient for nutrient in food_info if nutrient["nutrient"]["id"] == 1008), None)
        carbs_info = next((nutrient for nutrient in food_info if nutrient["nutrient"]["id"] == 1005), None)
        fats_info = next((nutrient for nutrient in food_info if nutrient["nutrient"]["id"] == 1004), None)

        protein = protein_info["amount"] if protein_info else 0.0
        fiber = fiber_info["amount"] if fiber_info else 0.0
        calorie = calorie_info["amount"] if calorie_info else 0.0
        carbs = carbs_info["amount"] if carbs_info else 0.0
        fats = fats_info["amount"] if fats_info else 0.0

        
        if not any(food['id'] == data["fdcId"] for food in recent_searches):
            recent_searches.append({
                "id": data["fdcId"],
                "name": food_name,
                "brand": data.get("brandName", None),
                "protein": protein,
                "fiber": fiber,
                "calorie": calorie,
                "carbs" : carbs,
                "fats" : fats
            })

        if len(recent_searches) > 4:
            recent_searches.pop(0)
        
        if "brandName" in data and "ingredients" in data:
            food_brand = data["brandName"]
            food_ingredients = data["ingredients"]
            return render_template('food.html', food_info=food_info, food_name=food_name, food_brand=food_brand, food_ingredients=food_ingredients)
        
        if "brandName" in data:
            food_brand = data["brandName"]
            return render_template('food.html', food_info=food_info, food_name=food_name, food_brand=food_brand)
        
        if "ingredients" in data:   
            food_ingredients = data["ingredients"]
            return render_template('food.html', food_info=food_info, food_name=food_name, food_ingredients=food_ingredients)
        
        if "brandName" not in data and "ingredients" not in data:
            return render_template('food.html', food_info=food_info, food_name=food_name)
        
    except requests.exceptions.RequestException as e:
        return jsonify(errMsg = str(e)), 500


# FUNCTION FOR SEARCHING A FOOD ITEM
@app.post('/foodsearch/')
def foodsearch():
    query = request.form.get("query")
    api_key = os.getenv('API_KEY')
    url = f'https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={query}&pageSize={10}'

    # Define the nutrient IDs of interest
    nutrient_ids = {
        1003: "protein",
        1004: "fats",
        1005: "carbs",
        1008: "calories"
    }

    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        foods = []

        # Process each food result
        for food in data["foods"]:
            food_info = {"id": food["fdcId"], "description": food["description"]}
            
            # Extract nutrient information
            nutrients = {nutrient["nutrientId"]: nutrient["value"] 
                         for nutrient in food.get("foodNutrients", [])
                         if nutrient["nutrientId"] in nutrient_ids}

            # Map extracted nutrients to their labels
            for nutrient_id, nutrient_name in nutrient_ids.items():
                food_info[nutrient_name] = nutrients.get(nutrient_id, 0.0)  # Default to 0.0 if missing
            
            # Include optional fields like brand if present
            food_info["brand"] = food.get("brandOwner", "Unknown")
            foods.append(food_info)
        
        return render_template('foodsearch.html', foods=foods)

    except requests.exceptions.RequestException as e:
        return jsonify(errMsg=str(e)), 500

    
@app.get('/foodsearch/')
def searchpage():
    
    return render_template('foodsearch.html')

# Route for profile page
@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login_page'))
    # loads default profile picture for the time being
    profile_picture = 'static/images/default-profile-pic.jpg'
    # meals = get_user_meals(user_id)
    # return meals=meals when repo is done
    meals = meal_repository.get_meal(user_id)
    
    return render_template('profile.html', profile_picture=profile_picture, meals=meals)

# Big Api Call 
# USDA FoodData Central 
@app.get('/food-list')
def food_list():
    api_key = os.getenv('API_KEY')
    url = f'https://api.nal.usda.gov/fdc/v1/foods/list?api_key={api_key}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json() 
        print(data)
        return data
    except requests.exceptions.RequestException as e:
        return jsonify(errMsg = str(e)), 500
    

# Starts the Flask application in debug mode
if __name__ == '__main__':
    app.run(debug=True)
