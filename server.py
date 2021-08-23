from model import connect_to_db
from flask import Flask, render_template, redirect, flash, session, request
from datetime import date as dt
import jinja2

app = Flask(__name__)

# make Jinja report undefined variables
app.jinja_env.undefined = jinja2.StrictUndefined

app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True

@app.route("/")
def hello():
    return render_template("frontpage.html")

@app.route("/recipes")
def show_recipes():
    """Return page showing all recipes contained in database"""

    recipe_list = ['recipe', 'recipe', 'recipe','recipe','recipe','recipe','recipe','recipe','recipe','recipe']
    return render_template("recipes.html", recipe_list=recipe_list)

@app.route("/homepage")
def show_homepage():
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
    return render_template("homepage.html", today=today, day_of_week=day_of_week)

@app.route("/acct")
def show_acct_info():
    return render_template("acct_info.html")

@app.route("/list")
def show_list():
    """show all ingredients needed for recipes in weekly planner"""

    shopping_list = ['apple', 'orange', 'grape', 'watermelon']
    return render_template("shopping_list.html", shopping_list=shopping_list)


if __name__ == "__main__":
    connect_to_db(app)
    app.run(debug=True, host="0.0.0.0")