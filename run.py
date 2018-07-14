import os
from datetime import datetime
from flask import Flask, redirect, render_template, request, flash, request, url_for, session
from flask_pymongo import PyMongo
import bcrypt
from game_engine import create_player, get_game_state
from territories import territories
from wtforms import StringField, SubmitField, SelectField, HiddenField, TextField, FieldList, FormField
from initial_game_state import *
from wtforms.validators import DataRequired
import pymongo
from forms import RegistrationForm, LoginForm
from players import players
from orders import initial_orders

app = Flask(__name__)
app.config['SECRET_KEY'] = "^b$#s3uwbysorx2f3uowzzlxucw8j3stqu7!^452*&i-&ab3g%"

# Vars ------------------------------------------

game_state = {}

# -----------------------------------------------


# Mongo -----------------------------------------

app.config["MONGO_DBNAME"] = "diplomacydb"
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

mongo = PyMongo(app)

# -----------------------------------------------


# Functions -------------------------------------

def clear_db():
    mongo.db.pieces.remove({})
    mongo.db.users.remove({})
    mongo.db.ownership.remove({})
    mongo.db.orders.remove({})
    mongo.db.nations.remove({})
    mongo.db.game_properties.remove({})

def populate_users():
    mongo.db.users.remove({})
    users = mongo.db.users
    for player in players:
        users.insert(player)
        
def fill_out_orders():
    mongo.db.orders.remove({})
    orders = mongo.db.orders
    for order in initial_orders:
        orders.insert(order)
    
def initialise_game_db():
    clear_db()
    pieces = mongo.db.pieces
    for piece in initial_pieces:
        pieces.insert(piece)
    nations = mongo.db.nations
    for nation in initial_nations:
        nations.insert(nation)
    mongo.db.ownership.insert(initial_ownership)
    mongo.db.game_properties.insert(initial_game_properties)
    flash('Game initialised!', 'success')
    return redirect(url_for("register"))
    
def start_game():
    mongo.db.game_properties.update_one({}, {"$set": {"game_started": True}})
    flash('Game Started!', 'success')
    return get_game_state()
    
def process_orders():
    flash('Orders proccessed!', 'success')

def are_seven_players_registered():
    return mongo.db.users.count() >= 7
    
def filter_pieces_by_user(username):
    user = mongo.db.users.find_one({"username": username})
    pieces = mongo.db.pieces.find()
    return [piece for piece in pieces if piece["owner"] == user["nation"]]
    
def create_order(request, pieces, game_state, username):
    for piece in pieces:
        order = {
            "origin": request.form[(piece["territory"] + "-origin")],
            "command": request.form[(piece["territory"] + "-command")],
            "target": request.form[(piece["territory"] + "-target")],
            "object": request.form[(piece["territory"] + "-object")],
            "year": game_state["game_properties"]["year"],
            "phase": game_state["game_properties"]["phase"],
            "nation": mongo.db.users.find_one({"username": username})["nation"]
        }
        mongo.db.orders.insert(order)
        mongo.db.users.update_one({"username": username}, {"$set": {"orders_finalised": True}})
    flash('Orders finalised!', 'success')
        

def write_to_file(filename, data):
    with open(filename, "a") as file:
        file.writelines(data)

def add_announcements(username, announcement):
    announcement = "({}) {}: {}\n".format(datetime.now().strftime("%H:%M:%S"), username, announcement)
    write_to_file("data/announcements.txt", announcement)
    
def get_all_announcements():
    announcements_list = []
    with open("data/announcements.txt", "r") as announcements: 
        announcements_list = announcements.readlines()
    return announcements_list
    
def get_pieces():
    return mongo.db.pieces.find()

# -----------------------------------------------
    
    
    
# ROUTES ==========================================================================================

# board -----------------------------------------

@app.route("/")
def board():
    game_state = get_game_state()
    
    # if no players are registered, initialise db
    if not mongo.db.users.count():
        return initialise_game_db()
        
    # if seven players are registered, start game
    if mongo.db.users.count() >= 7 and not game_state["game_properties"]["game_started"]:
        game_state = start_game()
        
    # if all players have finalised order, process orders
    if all(user["orders_finalised"] for user in mongo.db.users.find()):
        # unfinalise_users()
        # save_orders_to_log()
        process_orders()
        # increment year
        #  increment phase
        # clear orders
    
    return render_template("board.html", game_state = game_state, session = session)
    
# -----------------------------------------------


# register --------------------------------------
    
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        
        users = mongo.db.users
        # only finds duplicate usernames. should find duiplicate emails too
        existing_user = users.find_one({"username": request.form["username"]})
        
        # refactor?
        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form["password"].encode('utf-8'), bcrypt.gensalt())
            nation = create_player(request.form["username"])
            users.insert({"username": request.form["username"], "email": request.form["email"], "password": hashpass, "nation": nation })
            session["username"] = request.form["username"]
            flash('Account created for {}!'.format(form.username.data), 'success')
            return redirect(url_for('board'))
        flash('That username already exists', 'danger')
        
    return render_template("register.html", form = form, game_state = get_game_state())
    
# -----------------------------------------------
    
    
# login -----------------------------------------
    
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        
        users = mongo.db.users
        login_user = users.find_one({"email": request.form["email"]})
        
        # are my log in credentials secure?
        if login_user:
            if bcrypt.hashpw(request.form["password"].encode("utf-8"), login_user["password"]) == login_user["password"]:
                session["username"] = login_user["username"]
                flash('You have been logged in!', 'success')
                return redirect(url_for('board'))
            else:
                flash('Login unsuccessful. Invalid username/password combinationA.', 'danger')
        else:
            flash('Login unsuccessful. Invalid username/password combinationB.', 'danger')
    return render_template("login.html", form = form, game_state = get_game_state())
    
# -----------------------------------------------


# logout -----------------------------------------
    
@app.route("/logout", methods=["GET", "POST"])
def logout():
    session["username"] = None
    flash('You have been logged out.', 'success')
    return redirect(url_for('board'))
    
# -----------------------------------------------


# orders ----------------------------------------
    
@app.route("/orders", methods=["GET", "POST"])
def orders():
    game_state = get_game_state()
    username = session["username"]
    if mongo.db.users.find_one({"username": username })["orders_finalised"]:
        return redirect(url_for("finalised"))
    
    pieces = filter_pieces_by_user(username)
        
    if request.method == "POST":
        create_order(request, pieces, game_state, username)
        return redirect(url_for('board'))
            
    return render_template("orders.html", pieces = pieces, territories = territories, game_state = game_state)
    
# -----------------------------------------------


# finalised -------------------------------------
    
@app.route("/finalised",)
def finalised():
    game_state = get_game_state()
    return render_template("finalised.html", game_state = game_state)
    
# -----------------------------------------------


# edit orders -----------------------------------
    
@app.route("/edit_orders", methods=["GET", "POST"])
def edit_orders():
    username = session["username"]
    
    if not mongo.db.users.find_one({"username": username })["orders_finalised"]:
        return "you have not submitted your orders"
    game_state = get_game_state()
    pieces = filter_pieces_by_user(username)
        
    if request.method == "POST":
        # edit_order(request, pieces, game_state, username)
        return redirect(url_for('board'))
            
    return render_template("edit_orders.html", pieces = pieces, territories = territories, game_state = game_state)
    
# -----------------------------------------------


# announcements ---------------------------------
    
@app.route("/announcements/")
def announcements():
    announcements = get_all_announcements()
    return render_template("announcements.html", announcements = announcements)
    
# -----------------------------------------------
    
    
# add announcements ----------------------------- 

@app.route("/announcements/<username>/<announcement>")
def post_announcement(username, announcement):
    add_announcements(username, announcement)
    return redirect("announcements")
    
# -----------------------------------------------


# populate --------------------------------------

@app.route("/populate")
def populate():
    populate_users()
    return redirect(url_for('board'))
    
# -----------------------------------------------


# fill_orders -----------------------------------

@app.route("/fill")
def fill():
    fill_orders()
    return redirect(url_for('board'))
    
# -----------------------------------------------



# process_orders -----------------------------------

@app.route("/process")
def process():
    process_orders()
    return redirect(url_for('board'))
    
# -----------------------------------------------


# initialise ------------------------------------

@app.route("/initialise")
def initialise():
    initialise_game_db()
    return redirect(url_for('board'))
    
# -----------------------------------------------


if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), 
            port=int(os.getenv('PORT', 8080)), 
            debug=True)