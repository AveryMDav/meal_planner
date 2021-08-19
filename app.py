from flask import Flask, render_template, redirect, flash, session, request
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
    return render_template("homepage.html")

@app.route("/list")
def show_list():
    return render_template("shopping_list.html")

@app.route("/acct")
def show_user_info():
    return render_template("acct_info.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")