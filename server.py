from model import connect_to_db, db, recipe_ingredients, recipes, scheduled_item, user, weekly_planner, base_food
from util import items_info, calculate_cal
from flask import Flask, render_template, redirect, flash, session, request
from datetime import date, datetime, timedelta
import jinja2

app = Flask(__name__)

app.secret_key = "w\x9f\xfd\x8e~\x0cO\x9c\xb5\xd5\x93[\x9b@\n\x9eJ6XC\xde\xc8\x1f\x80"

# make Jinja report undefined variables
app.jinja_env.undefined = jinja2.StrictUndefined

app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True

@app.route("/")
def show_front_page():
    """loads front page of app"""

    if "user" in session:
        return redirect("/homepage")

    return render_template("frontpage.html")

@app.route("/", methods=["POST"])
def process_log_in():
    """logs user into session"""

    if request.method == "POST":
        email = request.form["email"].lower()
        password = request.form["password"]
        if user.query.filter_by(email=email).first():
            account_user = user.query.filter_by(email=email).first()
            if account_user.password == password:
                flash("Logged In Succesfully")
                session["user"] = f"{account_user.email}"
                return redirect("/homepage")
            else:
                flash("Incorrect Password")
                return redirect("/")
        else:
            flash("Email not found")
            return redirect("/")

@app.route("/recipes", methods=["POST", "GET"])
def show_recipes():
    """Return page showing all recipes contained in database"""

    if "user" not in session:
        return redirect("/")

    current_user = user.query.filter_by(email=session["user"]).first()

    if request.method == "POST":

        new_recipe = recipes(
            user_id = current_user.user_id,
            recipe_name = request.form["recipe_name"],
            directions = request.form["directions"],
            cal_per_serving = request.form["serving_size"]
        )
    
        db.session.add(new_recipe)
        db.session.commit()

        new_recipe_id = new_recipe.recipes_id
        new_ingredients = []
        quantity_list = []

        for key, value in request.form.items():
            if "ingredient" in key:
                new_ingredients.append(value)
            if "quantity" in key:
                quantity_list.append(value)
        
        ingredients = zip(new_ingredients, quantity_list)

        for item in ingredients:
            new_ingredient = recipe_ingredients(
                quantity = item[1],
                name = item[0],
                recipes_id = new_recipe_id
            )

            db.session.add(new_ingredient)
            db.session.commit()
    
    all_recipes = recipes.query.filter_by(user_id=current_user.user_id).all()
    recipe_names = [object.recipe_name for object in all_recipes]
    directions = [object.directions for object in all_recipes]

    return render_template("recipes.html", recipe_names=recipe_names, directions=directions, all_recipes=all_recipes)

@app.route("/recipe_info/<recipes_id>", methods=["POST", "GET"])
def show_recipe_info(recipes_id):
    """render information for single recipe"""

    assigned_day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    meal_types = ["Breakfast", "Lunch", "Dinner", "Snacks"]
    recipe = recipes.query.filter_by(recipes_id=recipes_id).first()
    current_user = user.query.filter_by(email=session["user"]).first()
    current_planner = weekly_planner.query.filter_by(user_id=current_user.user_id).first()

    ingredients_query = db.session.query(recipe_ingredients.quantity, recipe_ingredients.name, recipes.recipes_id).join(recipes).filter(recipe_ingredients.recipes_id == recipes.recipes_id).all()

    ingredients = []

    for item in ingredients_query:
        if item[2] == recipe.recipes_id:
            ingredients.append(item)

    if request.method == "POST":
        recipe_meal = scheduled_item(
            meal_day = request.form["day"],
            meal_type = request.form["meal"],
            serving_size = request.form["serving_size"],
            weekly_planner_id = current_planner.weekly_planner_id,
            recipes_id = recipe.recipes_id
        )

        db.session.add(recipe_meal)
        db.session.commit()

    return render_template("recipe_info.html", display_recipe=recipe, ingredients_list=ingredients, assigned_day=assigned_day, meal_types=meal_types)

@app.route("/homepage", methods=["POST", "GET"])
def show_homepage():
    """Get returns the users weekly planner"""

    if "user" not in session:
        return redirect("/")
    #makes sure the user is logged in before accessing website


    today = date.today().strftime('%b/%d/%Y')
    dt = datetime.strptime(today, '%b/%d/%Y')
    start = dt - timedelta(days=dt.weekday())
    end = start + timedelta(days=6)
    #creates logic for the weekly planner assigned week

    current_user = user.query.filter_by(email=session["user"]).first()
    current_planner = weekly_planner.query.filter_by(user_id=current_user.user_id).first()

    if current_planner:
        pass
    else:
        planner = weekly_planner(
            user_id = current_user.user_id,
            date = start.strftime('%b/%d/%Y')
        )
        
        db.session.add(planner)
        db.session.commit()
        return redirect("/homepage")
    #creates the weekly planner for the current week

    assigned_day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    meal_types = ["Breakfast", "Lunch", "Dinner", "Snacks"]
    #lists to loop through in homepage.html for weekdays and meal types

    day_of_week = date.today().weekday()
    if day_of_week == 0:
            day_of_week = "Monday"
    elif day_of_week == 1:
            day_of_week = "Tuesday"
    elif day_of_week == 2:
            day_of_week = "Wednesday"
    elif day_of_week == 3:
            day_of_week = "Thursday"
    elif day_of_week == 4:
            day_of_week = "Friday"
    elif day_of_week == 5:
            day_of_week = "Saturday"
    else:
            day_of_week = "Sunday"
    #creates logic for day of week on homepage.html 

    info = None

    if request.method == "POST" and "form-submit2" in request.form:

        if base_food.query.filter_by(item_name=request.form["name"]).first():
            pass
        else:
            base_item = base_food(
                item_name = request.form["name"],
                calorie_count = request.form["cal"]
            )
            db.session.add(base_item)
            db.session.commit()
        #adds selected food to the base_foods table to be used by weekly planner

        name_query = base_food.query.filter_by(item_name=request.form["name"]).first()

        meal_item = scheduled_item(
            meal_day = request.form["day"],
            meal_type = request.form["meal"],
            weight = request.form["weight"],
            base_food_id = name_query.base_food_id,
            weekly_planner_id = current_planner.weekly_planner_id
        )

        db.session.add(meal_item)
        db.session.commit()
        #schedules selected base food into the weekly planner

    elif request.method == "POST" and "form-submit" in request.form:

        info = items_info(request.form["search"])
    #Uses Edamam API to search for base foods

    planner_items = db.session.query(scheduled_item.meal_day, scheduled_item.meal_type, base_food.item_name, base_food.calorie_count, scheduled_item.weight).join(base_food).filter(scheduled_item.base_food_id == base_food.base_food_id, scheduled_item.weekly_planner_id == current_planner.weekly_planner_id).all()
    #query for info from the scheduled items table to populate weekly planner

    cal_planner_items = []

    for tuple_to_list in planner_items:
        tuple_to_list = list(tuple_to_list)
        cal = int(calculate_cal(tuple_to_list[3], tuple_to_list[4]))
        tuple_to_list.pop()
        tuple_to_list.pop()
        tuple_to_list.append(cal)
        cal_planner_items.append(tuple_to_list)
    #calculating the calorie count based on weight in grams of meal

    Monday_total = 0
    Tuesday_total = 0
    Wednesday_total = 0
    Thursday_total = 0
    Friday_total = 0
    Saturday_total = 0
    Sunday_total = 0

    for meal_info in cal_planner_items:
        if meal_info[0] == "Monday":
            Monday_total = Monday_total + meal_info[3]
        elif meal_info[0] == "Tuesday":
            Tuesday_total = Tuesday_total + meal_info[3]
        elif meal_info[0] == "Wednesday":
            Wednesday_total = Wednesday_total + meal_info[3]
        elif meal_info[0] == "Thursday":
            Thursday_total = Thursday_total + meal_info[3]
        elif meal_info[0] == "Friday":
            Friday_total = Friday_total + meal_info[3]
        elif meal_info[0] == "Saturday":
            Saturday_total = Saturday_total + meal_info[3]
        else:
            Sunday_total = Sunday_total + meal_info[3]
    #calculate total calorie count for each day

    daily_cal_goal = db.session.query(user.dcg).filter(user.email == session['user']).first()


    return render_template("homepage.html", today=today, day_of_week=day_of_week, start=start.strftime('%b/%d/%Y'), end=end.strftime('%b/%d/%Y'), info=info, assigned_day=assigned_day, meal_types=meal_types, planner_items=cal_planner_items, Monday_total=Monday_total, Tuesday_total=Tuesday_total, Wednesday_total=Wednesday_total, Thursday_total=Thursday_total, Friday_total=Friday_total, Saturday_total=Saturday_total, Sunday_total=Sunday_total, daily_cal_goal=daily_cal_goal[0])

@app.route("/acct")
def show_acct_info():
    """lists out account info for user, allows them to update their information, and change their password"""

    if "user" not in session:
        return redirect("/")


    user_search = user.query.filter_by(email=session["user"]).first()

    user_info = {
        "Name": f"{user_search.first_name} {user_search.last_name}",
        "Email": f"{user_search.email}",
        "Phone Number": f"{user_search.phone_number}",
        "Weight": f"{user_search.weight}",
        "Daily Calorie Goal": f"{user_search.dcg}"
    }

    return render_template("acct_info.html", user_info=user_info)

@app.route("/update")
def update_acct_info():
    """allows user to update their account information"""

    if "user" not in session:
        return redirect("/")
    
    user_search = user.query.filter_by(email=session["user"]).first()

    user_info = {
        "Name": f"{user_search.first_name} {user_search.last_name}",
        "Email": f"{user_search.email}",
        "Phone Number": f"{user_search.phone_number}",
        "Weight": f"{user_search.weight}",
        "Daily Calorie Goal": f"{user_search.dcg}"
    }

    return render_template("update_acct_info.html", user_info=user_info)

@app.route("/list")
def show_list():
    """show all ingredients needed for recipes in weekly planner"""

    if "user" not in session:
        return redirect("/")

    today = date.today().strftime('%b/%d/%Y')
    dt = datetime.strptime(today, '%b/%d/%Y')
    start = dt - timedelta(days=dt.weekday())

    current_user = user.query.filter_by(email = session["user"]).first()
    current_planner = weekly_planner.query.filter_by(user_id = current_user.user_id, date=start.strftime('%b/%d/%Y')).first()
    
    planner_items = db.session.query(base_food.item_name).join(scheduled_item).filter(scheduled_item.base_food_id == base_food.base_food_id, scheduled_item.weekly_planner_id == current_planner.weekly_planner_id).all()

    shopping_list = []

    for item in planner_items:
        shopping_list.append(item[0])
    
    print(shopping_list)

    return render_template("shopping_list.html", shopping_list=set(shopping_list))

@app.route("/sign_up")
def show_sign_up():

    """Show sign up page"""

    return render_template("sign_up.html")

@app.route("/sign_up", methods=["POST"])
def process_sign_up():
    """Creates new user information and check for existing user"""

    if request.method == "POST":
        email =  request.form["email"].lower()
        password = request.form["password"]
        first_name = request.form["first-name"]
        last_name = request.form["last-name"]
        phonenumber = request.form["phonenumber"]
        weight = request.form["weight"]
        goal = request.form["goal"]
        if user.query.filter_by(email=email).first():
            flash("User already exists")
            return redirect("/sign_up")
        else:
            new_user = user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone_number=phonenumber,
                weight=weight,
                dcg=goal
            )

            db.session.add(new_user)
            db.session.commit()
            flash("Sign Up Successful")
            return redirect("/")

@app.route("/log_out")
def log_out():
    """deletes user out of session"""

    session.pop("user")
    flash("Logged Out")
    return redirect("/")



if __name__ == "__main__":
    connect_to_db(app)
    app.run(debug=True, host="0.0.0.0")