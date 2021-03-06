from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

#####################################################################

class user(db.Model):
    """Holds user information"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    password = db.Column(db.String(60), nullable=False)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    phone_number = db.Column(db.String(10))
    email = db.Column(db.String(60), unique=True)
    weight = db.Column(db.Integer)
    dcg = db.Column(db.Integer)

    def __repr__(self):
        return f"<User user_id={self.user_id} name={self.first_name} {self.last_name} email={self.email} phone number={self.phone_number}>"

class weekly_planner(db.Model):
    """table for building out my weekly planner"""

    __tablename__ = "weekly_planner"

    weekly_planner_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=date.today().strftime('%d/%b/%Y'))

    users = db.relationship("user", backref=db.backref("weekly_planner", order_by=weekly_planner_id))

    def __repr__(self):
        return f"<planner weekly planner_id={self.weekly_planner_id} user_id={self.user_id}>"

class base_food(db.Model):
    """table for base foods like bananas, eggs, etc"""

    __tablename__ = "base_foods"

    base_food_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    item_name = db.Column(db.String(60), unique=True, nullable=False)
    calorie_count = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<base_food food={self.item_name} calories={self.calorie_count}>"

class scheduled_item(db.Model):
    """table for scheduling items in weekly planner"""

    __tablename__ = "scheduled_items"

    scheduled_item_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    meal_day = db.Column(db.String(10), nullable=False)
    meal_type = db.Column(db.String(10), nullable=False)
    weight = db.Column(db.Integer)
    serving_size = db.Column(db.Integer)
    base_food_id = db.Column(db.Integer, db.ForeignKey('base_foods.base_food_id'))
    weekly_planner_id = db.Column(db.Integer, db.ForeignKey('weekly_planner.weekly_planner_id'), nullable=False)
    recipes_id = db.Column(db.Integer, db.ForeignKey('recipes.recipes_id'))

    base_food = db.relationship("base_food", backref=db.backref("scheduled_items", order_by=scheduled_item_id))
    weekly_planner = db.relationship("weekly_planner", backref=db.backref("scheduled_items", order_by=scheduled_item_id))
    recipes = db.relationship("recipes", backref=db.backref("scheduled_items", order_by=scheduled_item_id))

    def __repr__(self):
        return f"<scheduled_item day={self.meal_day} type={self.meal_type} meal={self.base_food_id} recipe={self.recipes_id}>"

class recipes(db.Model):
    """Holds all recipes saved in database"""

    __tablename__ = "recipes"

    recipes_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False) 
    recipe_name = db.Column(db.String(60), nullable=False)
    directions = db.Column(db.Text, nullable=False)
    cal_per_serving = db.Column(db.Integer)

    users = db.relationship("user", backref=db.backref("recipes", order_by=recipes_id))

    def __repr__(self):
        return f"<recipes recipe={self.recipe_name}>"

class recipe_ingredients(db.Model):
    """connects the recipes and base_food tables"""

    __tablename__ = "recipe_ingredients"

    recipes_food_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    quantity = db.Column(db.String(60), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    recipes_id = db.Column(db.Integer, db.ForeignKey('recipes.recipes_id'), nullable=False)

    recipes = db.relationship("recipes", backref=db.backref("recipe_ingredients", order_by=recipes_food_id))

    def __repr__(self):
        return f"<recipe_ingredients recipe id={self.recipes_id} quantity={self.quantity} name={self.name}>"



#####################################################################
def connect_to_db(app):
    """Connect the database to the Flask app"""

    # app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:TwentyFour%404@localhost/mealplanner'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://cbscqbdkzfnlae:42030f6548e08d6c4b94bc3c72d4fcf0f2f2a8f8ffc1dcff9a3c1d3df480334c@ec2-54-83-137-206.compute-1.amazonaws.com:5432/dfpqoqcgdo2ldv'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)

if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    print("Connected to DB")