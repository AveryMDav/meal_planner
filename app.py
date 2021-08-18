from flask import Flask, render_template, redirect, flash, session, request
import jinja2

app = Flask(__name__)

# make Jinja report undefined variables
app.jinja_env.undefined = jinja2.StrictUndefined

@app.route("/")
def hello():
    return render_template("marketing_page.html")

@app.route("/recipes")
def render_recipes():
    return render_template("recipes_page.html")


if __name__ == "__main__":
    app.run()