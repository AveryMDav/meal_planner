from model import connect_to_db, db, user
from util import items_info
from flask import Flask, render_template, redirect, flash, session, request
from datetime import date as dt
import jinja2

app = Flask(__name__)

app.secret_key = "w\x9f\xfd\x8e~\x0cO\x9c\xb5\xd5\x93[\x9b@\n\x9eJ6XC\xde\xc8\x1f\x80"

# make Jinja report undefined variables
app.jinja_env.undefined = jinja2.StrictUndefined

app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True

@app.route("/")
def show_front_page():

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
                session["user"] = f"{account_user.first_name} {account_user.last_name}"
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

    recipe_list = ['recipe', 'recipe', 'recipe','recipe','recipe','recipe','recipe','recipe','recipe','recipe']
    return render_template("recipes.html", recipe_list=recipe_list)

@app.route("/homepage", methods=["POST", "GET"])
def show_homepage(info=None):
    if "user" not in session:
        return redirect("/")
    
    if request.method == "POST":
        item = request.form["meal"]
        info = items_info(item)
        
        result = info

    today = dt.today().strftime("%B %d, %Y")
    day_of_week = dt.today().weekday()

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
    return render_template("homepage.html", today=today, day_of_week=day_of_week, result=result)

@app.route("/acct")
def show_acct_info():
    if "user" not in session:
        return redirect("/")

    return render_template("acct_info.html")

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