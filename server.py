from werkzeug.wrappers.request import PlainRequest
from model import connect_to_db, db, recipes, scheduled_item, user, weekly_planner, base_food
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

@app.route("/recipes")
def show_recipes():
    """Return page showing all recipes contained in database"""
    if "user" not in session:
        return redirect("/")

    all_recipes = recipes.query.all()
    recipe_names = [object.recipe_name for object in all_recipes]
    directions = [object.directions for object in all_recipes]

    return render_template("recipes.html", recipe_names=recipe_names, directions=directions, all_recipes=all_recipes)

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

    current_planner = weekly_planner.query.filter_by(date=start).first()
    current_user = user.query.filter_by(email=session["user"]).first()

    if current_planner:
        pass
    else:
        planner = weekly_planner(
            user_id = current_user.user_id,
            date = start.strftime('%b/%d/%Y')
        )
        
        db.session.add(planner)
        db.session.commit()
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
            base_food_id = name_query.base_food_id,
            weekly_planner_id = current_planner.weekly_planner_id
        )

        db.session.add(meal_item)
        db.session.commit()
        #schedules selected base food into the weekly planner

    elif request.method == "POST" and "form-submit" in request.form:

        info = items_info(request.form["search"])
    #Uses Edamam API to search for base foods

    planner_items = scheduled_item.query.filter_by(weekly_planner_id=current_planner.weekly_planner_id).all()
    planner_items_dict = {}

    for item in planner_items:
        base_food_query = base_food.query.filter_by(base_food_id=item.base_food_id).first()
        food_name = base_food_query.item_name
        food_cal = base_food_query.calorie_count
        planner_items_dict[food_name] = food_cal, item.meal_day, item.meal_type
    
    for key, value in planner_items_dict.items():
        print(key, value[0], value[1], value[2])

    return render_template("homepage.html", today=today, day_of_week=day_of_week, start=start.strftime('%b/%d/%Y'), end=end.strftime('%b/%d/%Y'), info=info, assigned_day=assigned_day, meal_types=meal_types, planner_items=planner_items, planner_items_dict=planner_items_dict)

@app.route("/acct")
def show_acct_info():
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

@app.route("/list")
def show_list():
    """show all ingredients needed for recipes in weekly planner"""

    if "user" not in session:
        return redirect("/")

    shopping_list = ['apple', 'orange', 'grape', 'watermelon']
    return render_template("shopping_list.html", shopping_list=shopping_list)

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