from re import search

from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# --------------------------------
# DATABASE SETUP
# --------------------------------

def init_db():

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Users Table

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        last_login TEXT
    )
""")
# Reports Table

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            bmi REAL,
            calories INTEGER,
            goal TEXT,
            progress REAL,
            report_date TEXT
        )
    """)

    conn.commit()
    conn.close()



init_db()

# --------------------------------
# HOME PAGE
# --------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------
# LOGIN PAGE
# --------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()

        if user:

            from datetime import datetime

            login_time = datetime.now().strftime("%Y-%m-%d")

            cursor.execute(
                "UPDATE users SET last_login=? WHERE username=?",
                (login_time, username)
            )

            conn.commit()
            conn.close()

            return redirect(url_for("form_page"))

        else:

            conn.close()

            return "Invalid Username or Password"

    return render_template("login.html")



# --------------------------------
# SIGNUP PAGE
# --------------------------------

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        try:

            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )

            conn.commit()
            conn.close()

            return redirect(url_for("login"))

        except:

            conn.close()
            return "Username already exists!"

    return render_template("signup.html")
# --------------------------------
# ADMIN LOGIN
# --------------------------------

@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":

            return redirect(url_for("admin_dashboard"))

        else:
            return "Invalid Admin Credentials"

    return render_template("admin_login.html")
# --------------------------------
# ADMIN DASHBOARD
# --------------------------------
@app.route("/admin_dashboard")
def admin_dashboard():

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # SEARCH FEATURE

    search = request.args.get("search", "")

    if search:

        cursor.execute(
            "SELECT * FROM users WHERE username LIKE ?",
            ('%' + search + '%',)
        )

    else:

        cursor.execute("SELECT * FROM users")

    users = cursor.fetchall()

    cursor.execute("SELECT * FROM reports")
    reports = cursor.fetchall()
    conn.close()

    total_users = len(users)
    total_reports = len(reports)

    return render_template(
        "admin_dashboard.html",
        users=users,
        reports=reports,
        total_users=total_users,
        total_reports=total_reports
    )


# --------------------------------
# DELETE USER
# --------------------------------

@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM users WHERE id=?",
        (user_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin_dashboard"))


# --------------------------------
# FORM PAGE
# --------------------------------

@app.route("/form")
def form_page():
    return render_template("form.html")


# --------------------------------
# FOOD CALORIES FUNCTION
# --------------------------------

def calculate_food_calories(food, quantity, unit):

    pcs_foods = {
        "banana": 89,
        "apple": 95,
        "chapati": 120,
        "idli": 58,
        "dosa": 168,
        "egg": 78,
        "burger": 295,
        "sandwich": 250,
        "fish": 150
    }

    gram_foods = {
        "rice": 130,
        "oats": 389,
        "paneer": 265,
        "curd": 60,
        "dal": 116,
        "salad": 33,
        "soup": 40,

        "milk": 42,
        "buttermilk": 40,
        "fresh_juice": 45,
        "protein_shake": 120,
        "abc_juice": 50,

        "chicken": 239,
        "mutton": 294,
        "prawns": 99,
        "pizza": 266
    }

    if unit == "pcs":
        return quantity * pcs_foods.get(food, 0)

    elif unit == "grams":
        return (gram_foods.get(food, 0) * quantity) / 100

    elif unit == "ml":
        return (gram_foods.get(food, 0) * quantity) / 100

    elif unit == "litre":

        quantity = quantity * 1000
        return (gram_foods.get(food, 0) * quantity) / 100

    return 0


# --------------------------------
# WEEKLY DIET FUNCTION
# --------------------------------

def get_weekly_diet(goal, ingredients):

    weekly_plan = {

        "Monday": {
            "Breakfast": "Oats + Banana + Milk | Calories: 350 | Carbs: 45g | Fat: 8g | Protein: 15g",
            "Lunch": "Rice + Dal + Salad | Calories: 550 | Carbs: 70g | Fat: 10g | Protein: 18g",
            "Dinner": "Chapati + Chicken | Calories: 500 | Carbs: 35g | Fat: 12g | Protein: 32g"
        },

        "Tuesday": {
            "Breakfast": "Egg + Apple + Milk | Calories: 400 | Carbs: 30g | Fat: 14g | Protein: 22g",
            "Lunch": "Millet + Chicken + Vegetables | Calories: 560 | Carbs: 48g | Fat: 11g | Protein: 35g",
            "Dinner": "Soup + Paneer + Salad | Calories: 420 | Carbs: 20g | Fat: 15g | Protein: 24g"
        },

        "Wednesday": {
            "Breakfast": "Banana + Oats | Calories: 380 | Carbs: 50g | Fat: 9g | Protein: 14g",
            "Lunch": "Rice + Eggs + Peas | Calories: 530 | Carbs: 60g | Fat: 13g | Protein: 26g",
            "Dinner": "Chapati + Dal | Calories: 450 | Carbs: 42g | Fat: 8g | Protein: 16g"
        },

        "Thursday": {
            "Breakfast": "Apple + Toast | Calories: 360 | Carbs: 35g | Fat: 10g | Protein: 13g",
            "Lunch": "Millet + Chicken + Salad | Calories: 540 | Carbs: 40g | Fat: 12g | Protein: 34g",
            "Dinner": "Vegetable Soup + Eggs | Calories: 390 | Carbs: 18g | Fat: 11g | Protein: 21g"
        },

        "Friday": {
            "Breakfast": "Milk + Banana + Eggs | Calories: 410 | Carbs: 32g | Fat: 15g | Protein: 24g",
            "Lunch": "Rice + Dal + Carrot | Calories: 520 | Carbs: 66g | Fat: 9g | Protein: 17g",
            "Dinner": "Chapati + Paneer | Calories: 470 | Carbs: 30g | Fat: 14g | Protein: 25g"
        },

        "Saturday": {
            "Breakfast": "Oats + Apple | Calories: 370 | Carbs: 42g | Fat: 9g | Protein: 14g",
            "Lunch": "Chicken + Rice | Calories: 580 | Carbs: 52g | Fat: 13g | Protein: 36g",
            "Dinner": "Soup + Salad | Calories: 430 | Carbs: 28g | Fat: 8g | Protein: 18g"
        },

        "Sunday": {
            "Breakfast": "Eggs + Banana Smoothie | Calories: 390 | Carbs: 34g | Fat: 12g | Protein: 23g",
            "Lunch": "Rice + Chicken | Calories: 570 | Carbs: 58g | Fat: 12g | Protein: 35g",
            "Dinner": "Light Soup + Chapati | Calories: 410 | Carbs: 33g | Fat: 7g | Protein: 15g"
        }
    }

    return weekly_plan


# --------------------------------
# MAIN CALCULATION
# --------------------------------

@app.route("/calculate", methods=["POST"])
def calculate():

    # USER DETAILS

    weight = float(request.form["weight"])
    height = float(request.form["height"])
    age = int(request.form["age"])

    gender = request.form["gender"]
    goal = request.form["goal"]

    target_weight = float(request.form["target_weight"])

    current_weight = weight

    # FOOD DETAILS

    food1 = request.form["food1"]
    quantity1 = float(request.form["quantity1"])
    unit1 = request.form["unit1"]

    food2 = request.form["food2"]
    quantity2 = float(request.form["quantity2"])
    unit2 = request.form["unit2"]

    food3 = request.form.get("food3", "")

    if food3 != "":
        quantity3 = float(request.form["quantity3"])
        unit3 = request.form["unit3"]
    else:
        quantity3 = 0
        unit3 = ""

    ingredients = [food1, food2]

    if food3 != "":
        ingredients.append(food3)
  
   

    ingredients = [food1, food2, food3]

    weekly_diet = get_weekly_diet(goal, ingredients)

    # FOOD IMAGE

    food_image = request.files.get("food_image")

    if food_image and food_image.filename != "":

        if not os.path.exists("static/uploads"):
            os.makedirs("static/uploads")

        filename = food_image.filename.lower()

        image_path = "static/uploads/" + food_image.filename

        food_image.save(image_path)

    else:

        filename = ""
        image_path = ""

    # HEIGHT CONVERSION

    if height > 3:
        height = height / 100

    # BMI

    bmi = weight / (height * height)

    if bmi < 18.5:
        status = "Underweight"

    elif bmi < 24.9:
        status = "Normal Weight"

    elif bmi < 29.9:
        status = "Overweight"

    else:
        status = "Obese"

    # GOAL PLAN

    if goal == "weight_loss":

        goal_plan = "Focus on low-calorie foods and regular walking."

    elif goal == "weight_gain":

        goal_plan = "Focus on protein-rich foods and strength training."

    elif goal == "muscle_gain":

        goal_plan = "Focus on gym workouts and protein foods."

    else:

        goal_plan = "Maintain a balanced diet and exercise."

    # EXERCISE

    if status == "Underweight":

        exercise = "Strength training and proper sleep."

    elif status == "Normal Weight":

        exercise = "Walking, jogging and yoga."

    elif status == "Overweight":

        exercise = "Cardio workouts and cycling."

    else:

        exercise = "Walking and low-impact exercises."

    # DAILY CALORIES

    if gender == "male":
        calories = weight * 24

    else:
        calories = weight * 22

    # WATER

    water_intake = round(weight * 0.033, 2)

    water_glasses = round((water_intake * 1000) / 250)

    # FOOD CALORIES

    cal1 = calculate_food_calories(food1, quantity1, unit1)

    cal2 = calculate_food_calories(food2, quantity2, unit2)

    cal3 = calculate_food_calories(food3, quantity3, unit3)

    total_food_calories = round(cal1 + cal2 + cal3, 2)

    # AI FOOD SCANNER

    food_scan = "Unknown Food"

    scanner_calories = "Not Available"

    scanner_advice = "Food not available in database."

    if "banana" in filename:

        food_scan = "Banana"
        scanner_calories = 89

    elif "apple" in filename:

        food_scan = "Apple"
        scanner_calories = 95

    elif "burger" in filename:

        food_scan = "Burger"
        scanner_calories = 295

    elif "pizza" in filename:

        food_scan = "Pizza"
        scanner_calories = 266

    elif "egg" in filename:

        food_scan = "Egg"
        scanner_calories = 78

    elif "rice" in filename:

        food_scan = "Rice"
        scanner_calories = 130

    elif "chicken" in filename:

        food_scan = "Chicken"
        scanner_calories = 239

    if scanner_calories != "Not Available":

        if scanner_calories < 100:

            scanner_advice = "Healthy low-calorie food."

        elif scanner_calories < 200:

            scanner_advice = "Moderate calorie food."

        else:

            scanner_advice = "High calorie food."

    # PROGRESS TRACKER

    if current_weight > target_weight:

        progress = ((current_weight - target_weight) / current_weight) * 100

    else:

        progress = ((target_weight - current_weight) / target_weight) * 100

    progress = round(progress, 1)

    # RESULT PAGE
    from datetime import datetime

    today = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO reports
        (username, bmi, calories, goal, progress, report_date)

        VALUES (?, ?, ?, ?, ?, ?)
        """,

        (
            "Username",
            round(bmi, 2),
            round(calories),
            goal,
            progress,
            today
        )
    )

    conn.commit()
    conn.close()
    return render_template(

        "result.html",

        bmi=round(bmi, 2),
        status=status,
        calories=round(calories),

        goal_plan=goal_plan,
        exercise=exercise,

        water_intake=water_intake,
        water_glasses=water_glasses,

        food1=food1,
        quantity1=quantity1,
        unit1=unit1,
        cal1=round(cal1, 2),

        food2=food2,
        quantity2=quantity2,
        unit2=unit2,
        cal2=round(cal2, 2),

        food3=food3,
        quantity3=quantity3,
        unit3=unit3,
        cal3=round(cal3, 2),

        total_food_calories=total_food_calories,

        food_scan=food_scan,
        scanner_calories=scanner_calories,
        scanner_advice=scanner_advice,

        weekly_diet_plan=weekly_diet,

        image_path=image_path,

        current_weight=current_weight,
        target_weight=target_weight,
        progress=progress
    )


# --------------------------------
# LOGOUT
# --------------------------------

@app.route("/logout")
def logout():
    return redirect(url_for("login"))


# --------------------------------
# RUN APP
# --------------------------------

if __name__ == "__main__":
    app.run(debug=True)